from typing import Any, Callable, Generic, Sequence, cast
from src.service.types import TModel, TCreate, TUpdate, TResponse, TID, TFilter, TContext
from fastapi import HTTPException, Response, params
from src.service.crud_service import CrudService
from fastapi import Depends, Request, Path, Body
from fastapi.routing import APIRouter
from dataclasses import dataclass
from typing import Self  # Python 3.11+
from fastapi import status
from pydantic import BaseModel


class FilterString(BaseModel):
    pass


class SortingString(BaseModel):
    pass


@dataclass
class UrlParamDependency:
    type_: type[Any]
    depends_: Callable[..., Any] | None = None


@dataclass
class FilterContext:
    url_filter: Any | None = None
    url_sorting: Any | None = None
    url_pagination: Any | None = None


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
    ) -> None:
        self.service = service
        self.context_resolver = context_resolver
        self.prefix = prefix
        self.response_cls = response_cls
        self.router = APIRouter(prefix=self.prefix)

    def with_all(
        self,
        create_cls: type[TCreate],
        id_cls: type[TID],
        update_cls: type[TUpdate],
        filter_by_dep: UrlParamDependency | None = None,
        sort_by_dep: UrlParamDependency | None = None,
        pagination_dep: UrlParamDependency | None = None,
        filter_factory: Callable[[FilterContext], TFilter] | None = None,
    ) -> Self:
        return (
            self.with_get_by_id(id_cls=id_cls)
            .with_delete_by_id(id_cls=id_cls)
            .with_create(create_cls=create_cls)
            .with_get_all(
                filter_dependency=filter_by_dep,
                sort_dependency=sort_by_dep,
                filter_factory=filter_factory,
                pagination_dependency=pagination_dep,
            )
            .with_put(id_cls=id_cls, update_cls=update_cls)
            .with_exists_by_id(id_cls=id_cls)
        )

    def with_get_by_id(
        self,
        id_cls: type[TID],
        extra_dependencies: Sequence[params.Depends] | None = None,
        **kwargs: Any,
    ) -> Self:

        async def endpoint(
            request: Request,
            id: id_cls = Path(),  # type: ignore
            context: TContext = Depends(self.context_resolver),
        ):
            # return {"ok": "aa"}
            print("with_get_by_id::endpoint. id=", id, type(id))  # type: ignore

            return self.get_by_id_endpoint(id, context, request=request)  # type: ignore

        dependencies: Sequence[params.Depends] = []

        if extra_dependencies is not None:
            dependencies = extra_dependencies

        self.router.add_api_route(
            path="/{id}",
            methods=["GET"],
            response_model=self.response_cls | None,
            endpoint=endpoint,  # type: ignore
            dependencies=dependencies,
            **kwargs,
        )
        return self

    def with_delete_by_id(
        self,
        id_cls: type[TID],
        extra_dependencies: Sequence[params.Depends] | None = None,
        **kwargs: Any,
    ) -> Self:

        async def endpoint(
            request: Request,
            id: id_cls = Path(),  # type: ignore
            context: TContext = Depends(self.context_resolver),
        ):
            return self.delete_by_id_endpoint(id, context, request=request)  # type: ignore

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
        **kwargs: Any,
    ) -> Self:

        async def endpoint(
            request: Request,
            create_data: create_cls = Body(),  # type: ignore
            context: TContext = Depends(self.context_resolver),
        ):
            create_data_ = cast(TCreate, create_data)
            return self.create_endpoint(create_data_, context, request=request)

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
        filter_dependency: UrlParamDependency | None = None,
        sort_dependency: UrlParamDependency | None = None,
        pagination_dependency: UrlParamDependency | None = None,
        filter_factory: Callable[[FilterContext], TFilter] | None = None,
        extra_dependencies: Sequence[params.Depends] | None = None,
        **kwargs: Any,
    ) -> Self:

        def reolve_optional_depends(dep: UrlParamDependency | None) -> Callable[..., Any] | None:
            if dep is None:
                return None
            if dep.depends_ is None:
                return None
            return dep.depends_

        # handle optional dependency type
        filter_dependency_type_ = filter_dependency.type_ if filter_dependency else lambda: None
        sort_dependency_type_ = sort_dependency.type_ if sort_dependency else lambda: None
        pagination_dependency_type_ = (
            pagination_dependency.type_ if pagination_dependency else lambda: None
        )

        async def endpoint(
            request: Request,
            context: TContext = Depends(dependency=self.context_resolver),
            url_filter: filter_dependency_type_ = Depends(  # type: ignore
                dependency=reolve_optional_depends(filter_dependency)  # type: ignore
            ),  # type: ignore
            url_sorting: sort_dependency_type_ = Depends(reolve_optional_depends(sort_dependency)),  # type: ignore
            url_pagination: pagination_dependency_type_ = Depends(  # type: ignore
                dependency=reolve_optional_depends(pagination_dependency)  # type: ignore
            ),  # type: ignore
        ):

            filters = (
                filter_factory(
                    FilterContext(
                        url_filter=cast(Any, url_filter),
                        url_pagination=cast(Any, url_pagination),
                        url_sorting=cast(Any, url_sorting),
                    )
                )
                if filter_factory
                else None
            )

            return self.get_all_endpoint(context, request=request, filters=filters)

        dependencies: Sequence[params.Depends] = []

        if extra_dependencies is not None:
            dependencies = extra_dependencies

        self.router.add_api_route(
            path="/",
            methods=["GET"],
            response_model=list[self.response_cls],  # TODO: allow any response...
            endpoint=endpoint,  # type: ignore
            dependencies=dependencies,
            **kwargs,
        )
        return self

    def with_exists_by_id(
        self,
        id_cls: type[TID],
        extra_dependencies: Sequence[params.Depends] | None = None,
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
