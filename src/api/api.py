from typing import Any, Callable, Generic, Literal, Sequence, TypeAlias, TypeVar, cast
from src.service.types import TModel, TCreate, TUpdate, TResponse, TID, TFilter, TContext
from fastapi import HTTPException, Response, params
from src.service.crud_service import CrudService
from fastapi import Depends, Request, Path, Body
from fastapi.routing import APIRouter
from dataclasses import dataclass
from typing import Self  # Python 3.11+
from fastapi import status

T_DEPENDS = TypeVar("T_DEPENDS")


@dataclass
class UrlParamDependency(Generic[T_DEPENDS]):
    type_: type[T_DEPENDS]
    depends_: Callable[..., T_DEPENDS] | None = None


F = TypeVar("F", bound=Callable[..., Any])

EndpointDecoators: TypeAlias = dict[
    Literal["GET_ALL", "GET_BY_ID", "POST", "PUT", "DELETE_BY_ID", "HEAD", "EXISTS_BY_ID"],
    Callable[..., Any],
]


@dataclass
class ApiContainer(Generic[TModel, TCreate, TUpdate, TResponse, TID, TFilter, TContext]):
    fastapi_router: APIRouter
    service: CrudService[TModel, TCreate, TUpdate, TResponse, TID, TFilter, TContext]


class ApiBuilder(Generic[TModel, TCreate, TUpdate, TResponse, TID, TFilter, TContext]):
    def __init__(
        self,
        service: CrudService[TModel, TCreate, TUpdate, TResponse, TID, TFilter, TContext],
        context_resolver: Callable[[], TContext],
        prefix: str,
        response_cls: type[TResponse],
        endpoint_decorator: EndpointDecoators | None = None,
    ) -> None:
        self.service = service
        self.context_resolver = context_resolver
        self.prefix = prefix
        self.response_cls = response_cls
        self.router = APIRouter(prefix=self.prefix)
        self.endpoint_decorator = endpoint_decorator or {}

    def with_all(
        self,
        create_cls: type[TCreate],
        id_cls: type[TID],
        update_cls: type[TUpdate],
        extra_dependencies: Sequence[params.Depends] | None = None,
        filter_params: UrlParamDependency[T_DEPENDS] | None = None,
        filter_factory: Callable[[T_DEPENDS], TFilter] | None = None,
        endpoint_decorators: EndpointDecoators | None = None,
    ) -> Self:
        """
        Registers all CRUD endpoints for this router.

        Args:
            create_cls: Schema used for POST request body.
                Can be a Pydantic model (parsed from JSON body), a dataclass,
                or any callable FastAPI can resolve as a dependency.
            id_cls: Type of the resource ID (e.g. int, UUID).
            update_cls: Pydantic schema used for PUT request body.
            extra_dependencies: FastAPI dependencies applied to all endpoints (e.g. auth).
            filter_params: URL query param dependency for GET_ALL filtering.
            filter_factory: Converts filter params into a filter object passed to the service.
            endpoint_decorators: Optional decorators per endpoint type.
                Supported keys: GET_ALL, GET_BY_ID, POST, PUT, DELETE, EXISTS_BY_ID.
            Useful for caching GET endpoints, e.g. {"GET_BY_ID": cache(expire=60)}.
        """
        endpoint_decorators = endpoint_decorators or {}
        return (
            self.with_get_by_id(
                id_cls=id_cls,
                extra_dependencies=extra_dependencies,
                endpoint_decorator=endpoint_decorators.get("GET_BY_ID"),
            )
            .with_delete_by_id(
                id_cls=id_cls,
                extra_dependencies=extra_dependencies,
                endpoint_decorator=endpoint_decorators.get("DELETE_BY_ID"),
            )
            .with_create(
                create_cls=create_cls,
                extra_dependencies=extra_dependencies,
                endpoint_decorator=endpoint_decorators.get("POST"),
            )
            .with_get_all(
                filter_dependency=filter_params,
                filter_factory=filter_factory,
                extra_dependencies=extra_dependencies,
                endpoint_decorator=endpoint_decorators.get("GET_ALL"),
            )
            .with_put(
                id_cls=id_cls,
                update_cls=update_cls,
                extra_dependencies=extra_dependencies,
                endpoint_decorator=endpoint_decorators.get("PUT"),
            )
            .with_exists_by_id(
                id_cls=id_cls,
                extra_dependencies=extra_dependencies,
                endpoint_decorator=endpoint_decorators.get("EXISTS_BY_ID"),
            )
        )

    def with_get_by_id(
        self,
        id_cls: type[TID],
        extra_dependencies: Sequence[params.Depends] | None = None,
        endpoint_decorator: Callable[[F], F] | None = None,
        **kwargs: Any,
    ) -> Self:

        async def endpoint(
            request: Request,
            id: id_cls = Path(),  # type: ignore
            context: TContext = Depends(self.context_resolver),
        ):

            return self.get_by_id_endpoint(id, context, request=request)  # type: ignore

        endpoint_decorator = endpoint_decorator or self.endpoint_decorator.get("GET_BY_ID")

        if endpoint_decorator is not None:
            endpoint = endpoint_decorator(endpoint)  # type: ignore

        dependencies: Sequence[params.Depends] = []

        if extra_dependencies is not None:
            dependencies = extra_dependencies

        self.router.add_api_route(
            path="/{id}",
            methods=["GET"],
            response_model=self.response_cls,
            endpoint=endpoint,  # type: ignore
            dependencies=dependencies,
            **kwargs,
        )
        return self

    def with_delete_by_id(
        self,
        id_cls: type[TID],
        extra_dependencies: Sequence[params.Depends] | None = None,
        endpoint_decorator: Callable[[F], F] | None = None,
        **kwargs: Any,
    ) -> Self:

        async def endpoint(
            request: Request,
            id: id_cls = Path(),  # type: ignore
            context: TContext = Depends(self.context_resolver),
        ):
            return self.delete_by_id_endpoint(id, context, request=request)  # type: ignore

        endpoint_decorator = endpoint_decorator or self.endpoint_decorator.get("DELETE_BY_ID")

        if endpoint_decorator is not None:
            endpoint = endpoint_decorator(endpoint)  # type: ignore

        dependencies: Sequence[params.Depends] = []

        if extra_dependencies is not None:
            dependencies = extra_dependencies

        self.router.add_api_route(
            path="/{id}",
            methods=["DELETE"],
            response_model=self.response_cls,
            endpoint=endpoint,  # type: ignore
            dependencies=dependencies,
            **kwargs,
        )
        return self

    def with_create(
        self,
        create_cls: type[TCreate],
        extra_dependencies: Sequence[params.Depends] | None = None,
        endpoint_decorator: Callable[[F], F] | None = None,
        **kwargs: Any,
    ) -> Self:

        async def endpoint(
            request: Request,
            create_data: create_cls = Body(),  # type: ignore
            context: TContext = Depends(self.context_resolver),
        ):
            create_data_ = cast(TCreate, create_data)
            return self.create_endpoint(create_data_, context, request=request)

        endpoint_decorator = endpoint_decorator or self.endpoint_decorator.get("POST")

        if endpoint_decorator is not None:
            endpoint = endpoint_decorator(endpoint)  # type: ignore

        dependencies: Sequence[params.Depends] = []

        if extra_dependencies is not None:
            dependencies = extra_dependencies

        self.router.add_api_route(
            path="/",
            methods=["POST"],
            response_model=self.response_cls,
            endpoint=endpoint,  # type: ignore
            dependencies=dependencies,
            **kwargs,
        )
        return self

    def with_put(
        self,
        id_cls: type[TID],
        update_cls: type[TUpdate],
        extra_dependencies: Sequence[params.Depends] | None = None,
        endpoint_decorator: Callable[[F], F] | None = None,
        **kwargs: Any,
    ) -> Self:

        async def endpoint(
            request: Request,
            id: id_cls = Path(),  # type: ignore
            update_data: update_cls = Body(),  # type: ignore
            context: TContext = Depends(self.context_resolver),
        ):
            id_ = cast(TID, id)
            update_data_ = cast(TUpdate, update_data)
            return self.put_endpoint(id_, update_data_, context, request=request)

        endpoint_decorator = endpoint_decorator or self.endpoint_decorator.get("PUT")

        if endpoint_decorator is not None:
            endpoint = endpoint_decorator(endpoint)  # type: ignore

        dependencies: Sequence[params.Depends] = []

        if extra_dependencies is not None:
            dependencies = extra_dependencies

        self.router.add_api_route(
            path="/{id}",
            methods=["PUT"],
            response_model=self.response_cls,
            endpoint=endpoint,  # type: ignore
            dependencies=dependencies,
            **kwargs,
        )
        return self

    def with_get_all(
        self,
        filter_dependency: UrlParamDependency[T_DEPENDS] | None = None,
        filter_factory: Callable[[Any], TFilter] | None = None,
        extra_dependencies: Sequence[params.Depends] | None = None,
        endpoint_decorator: Callable[[F], F] | None = None,
        **kwargs: Any,
    ) -> Self:

        def reolve_optional_depends(
            dep: UrlParamDependency[T_DEPENDS] | None,
        ) -> Callable[..., Any] | None:
            if dep is None:
                return None
            if dep.depends_ is None:
                return None
            return dep.depends_

        # handle optional dependency type
        filter_dependency_type_ = filter_dependency.type_ if filter_dependency else lambda: None
        filter_dependency_call = reolve_optional_depends(filter_dependency)

        async def endpoint(
            request: Request,
            context: TContext = Depends(dependency=self.context_resolver),
            filter_params: filter_dependency_type_ = Depends(  # type: ignore
                dependency=filter_dependency_call  # type: ignore
            ),  # type: ignore
        ):

            filters = filter_factory(filter_params) if filter_factory else None

            return self.get_all_endpoint(context, request=request, filters=filters)

        endpoint_decorator = endpoint_decorator or self.endpoint_decorator.get("GET_ALL")
        if endpoint_decorator is not None:
            endpoint = endpoint_decorator(endpoint)  # type: ignore

        dependencies: Sequence[params.Depends] = []

        if extra_dependencies is not None:
            dependencies = extra_dependencies

        self.router.add_api_route(
            path="/",
            methods=["GET"],
            response_model=list[
                self.response_cls
            ],  # TODO: allow custom response. we need to support more than just lists of ...
            endpoint=endpoint,  # type: ignore
            dependencies=dependencies,
            **kwargs,
        )
        return self

    def with_exists_by_id(
        self,
        id_cls: type[TID],
        extra_dependencies: Sequence[params.Depends] | None = None,
        endpoint_decorator: Callable[[F], F] | None = None,
        **kwargs: Any,
    ) -> Self:

        async def endpoint(
            request: Request,
            id: id_cls = Path(),  # type: ignore
            context: TContext = Depends(self.context_resolver),
        ):

            if self.exists_by_id_endpoint(id, context, request=request):  # type: ignore
                return Response(status_code=status.HTTP_200_OK)
            else:
                return Response(status_code=status.HTTP_404_NOT_FOUND)

        endpoint_decorator = endpoint_decorator or self.endpoint_decorator.get("EXISTS_BY_ID")
        if endpoint_decorator is not None:
            endpoint = endpoint_decorator(endpoint)  # type: ignore

        dependencies: Sequence[params.Depends] = []

        if extra_dependencies is not None:
            dependencies = extra_dependencies

        self.router.add_api_route(
            path="/{id}",
            methods=["HEAD"],
            response_model=None,
            endpoint=endpoint,  # type: ignore
            dependencies=dependencies,
            **kwargs,
        )
        return self

    def build(self) -> ApiContainer[TModel, TCreate, TUpdate, TResponse, TID, TFilter, TContext]:
        assert len(self.router.routes) > 0, "No routes added. Forgot to call method 'with_all()'?"
        return ApiContainer(fastapi_router=self.router, service=self.service)

    def get_by_id_endpoint(self, id: TID, context: TContext, **kwargs: Any):
        entity = self.service.get_by_id(context, id)
        return entity

    def delete_by_id_endpoint(self, id: TID, context: TContext, **kwargs: Any):
        self.service.delete_by_id(context, id)
        return None

    def create_endpoint(self, create_data: TCreate, context: TContext, **kwargs: Any):
        entity = self.service.create(context, create_data)
        return entity

    def get_all_endpoint(self, context: TContext, filters: TFilter | None = None, **kwargs: Any):
        entity = self.service.get_all(context, filters=filters)
        return entity

    def put_endpoint(self, id: TID, update_data: TUpdate, context: TContext, **kwargs: Any):
        entity = self.service.update(context, id, update_data)

        if entity is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=f"Entity with id {id=} not found."
            )

        return entity

    def exists_by_id_endpoint(self, id: TID, context: TContext, **kwargs: Any):
        entity = self.service.exists_by_id(context, id)
        return entity
