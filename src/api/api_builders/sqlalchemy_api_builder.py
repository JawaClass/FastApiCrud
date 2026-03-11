from functools import wraps
from pydantic import BaseModel
from src.api.api import ApiBuilder, UrlParamDependency
from src.service.crud_service_mapper import SqlAlchemyAutoMapper
from src.service.sqlalchemy_crud_service import SqlAlchemyCrudService
from src.repository.sqlalchemy_crud_repository import (
    SqlAlchemyCrudRepository,
    SqlAlchemyCrudContext,
)
from typing import Any, Callable, Hashable
from src.repository.crud_filter import SaFilter
from sqlalchemy.orm import DeclarativeBase, InstrumentedAttribute, Session


def build_api[
    MODEL: DeclarativeBase,
    ID: Hashable,
    RESPONSE: BaseModel,
    UPDATE: BaseModel,
    CREATE: BaseModel,
    FILTER_URL
](
    model_cls: type[MODEL],
    prefix: str,
    id_column: InstrumentedAttribute[ID],
    response_cls: type[RESPONSE],
    update_cls: type[UPDATE],
    create_cls: type[CREATE],
    session_maker: Callable[[], Session],
    filter_factory: Callable[[FILTER_URL], SaFilter[MODEL]] | None = None, 
    filter_params: UrlParamDependency[FILTER_URL] | None = None,
):
    if filter_params is not None:
        assert filter_factory is not None
    if filter_factory is not None:
        assert filter_params is not None

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
    id_cls = model_cls.__table__.columns[id_column.key].type.python_type
    return api.with_all(
        create_cls=create_cls,
        id_cls=id_cls,
        update_cls=update_cls,
        filter_params=filter_params,
        filter_factory=filter_factory,
        endpoint_decorators={
            "GET_ALL": my_endpoint_decorator,
            "GET_BY_ID": my_endpoint_decorator
        }
    ).build()

def my_endpoint_decorator(f: Any):
    print('my_endpoint_decorator')
    @wraps(f) # MUST add wraps here, otherwiese signature is changed and fastapi looks as signature 
    def inner(*args: Any, **kwargs: Any):
        print("inner.............................", args, kwargs)
        return f(*args, **kwargs)
    return inner