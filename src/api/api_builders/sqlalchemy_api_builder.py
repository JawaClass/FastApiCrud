from pydantic import BaseModel
from src.api.api import ApiBuilder, FilterContext, UrlParamDependency
from src.service.crud_service_mapper import SqlAlchemyAutoMapper
from src.service.sqlalchemy_crud_service import SqlAlchemyCrudService
from src.repository.sqlalchemy_crud_repository import (
    SqlAlchemyCrudRepository,
    SqlAlchemyCrudContext,
)
from typing import Callable, Hashable
from src.repository.crud_filter import SaFilter
from sqlalchemy.orm import DeclarativeBase, InstrumentedAttribute, Session


def build_api[
    MODEL: DeclarativeBase,
    ID: Hashable,
    RESPONSE: BaseModel,
    UPDATE: BaseModel,
    CREATE: BaseModel,
](
    model_cls: type[MODEL],
    prefix: str,
    id_cls: type[ID],
    id_column: InstrumentedAttribute[ID],
    response_cls: type[RESPONSE],
    update_cls: type[UPDATE],
    create_cls: type[CREATE],
    session_maker: Callable[[], Session],
    filter_factory: Callable[[FilterContext], SaFilter[MODEL]] | None = None,
    filter_dependency: UrlParamDependency | None = None,
    sorting_dependency: UrlParamDependency | None = None,
    pagination_dependency: UrlParamDependency | None = None,
):

    Repository = SqlAlchemyCrudRepository[MODEL, ID]

    repo = Repository(model_class=model_cls, id_column=id_column)

    mapper = SqlAlchemyAutoMapper(
        model_cls=model_cls, response_cls=response_cls, create_cls=create_cls, update_cls=update_cls
    )

    service = SqlAlchemyCrudService(repository=repo, mapper=mapper)

    api = ApiBuilder(
        service=service,
        prefix=prefix,
        response_cls=response_cls,
        context_resolver=lambda: SqlAlchemyCrudContext(session=session_maker()),
    )

    return api.with_all(
        create_cls=create_cls,
        id_cls=id_cls,
        update_cls=update_cls,
        filter_by_dep=filter_dependency,
        sort_by_dep=sorting_dependency,
        pagination_dep=pagination_dependency,
        filter_factory=filter_factory,
    ).build()
