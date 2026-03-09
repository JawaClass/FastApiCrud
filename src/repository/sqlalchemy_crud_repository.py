from __future__ import annotations
from typing import Any, Iterable, TypeVar
from sqlalchemy import select, delete as sql_delete, func
from sqlalchemy.orm import Session, DeclarativeBase

# from typing_extensions import TypeVar
from src.repository.crud_repository import CrudRepository
from src.repository.crud_filter import Filter, SaFilter
from sqlalchemy.orm import InstrumentedAttribute
from typing import Generic
from dataclasses import dataclass

TModel = TypeVar("TModel", bound=DeclarativeBase)
ID = TypeVar("ID")
F = TypeVar("F", bound=Filter[Any])


@dataclass(frozen=True)
class SqlAlchemyCrudContext:
    session: Session


class SqlAlchemyCrudRepository(
    Generic[TModel, ID], CrudRepository[TModel, ID, SaFilter[TModel], SqlAlchemyCrudContext]
):
    def __init__(self, model_class: type[TModel], id_column: InstrumentedAttribute[ID]):
        self._model_class = model_class
        self._id_column = id_column

    def save(self, context: SqlAlchemyCrudContext, entity: TModel) -> TModel:
        context.session.add(entity)
        context.session.flush()
        context.session.refresh(entity)
        return entity

    def save_all(
        self, context: SqlAlchemyCrudContext, entities: Iterable[TModel]
    ) -> Iterable[TModel]:
        entities = list(entities)
        context.session.add_all(entities)
        context.session.flush()
        for entity in entities:
            context.session.refresh(entity)
        return entities

    def find_by_id(self, context: SqlAlchemyCrudContext, id: ID) -> TModel | None:
        return context.session.get(self._model_class, id)

    def exists_by_id(self, context: SqlAlchemyCrudContext, id: ID) -> bool:
        return self.find_by_id(context, id) is not None

    def find_all(
        self, context: SqlAlchemyCrudContext, filters: SaFilter[TModel] | None = None
    ) -> Iterable[TModel]:
        stmt = select(self._model_class)
        if filters:
            stmt = filters.apply(stmt)
        return context.session.execute(stmt).scalars().all()

    def find_all_by_id(self, context: SqlAlchemyCrudContext, ids: Iterable[ID]) -> Iterable[TModel]:
        ids = list(ids)
        return (
            context.session.execute(select(self._model_class).where(self._id_column.in_(ids)))  # type: ignore
            .scalars()
            .all()
        )

    def count(self, context: SqlAlchemyCrudContext, filters: SaFilter[TModel] | None = None) -> int:
        stmt = select(self._model_class)
        if filters:
            stmt = filters.apply(stmt)

        stmt = select(func.count()).select_from(stmt.subquery())

        result = context.session.execute(stmt).scalar()
        return result or 0

    def delete(self, context: SqlAlchemyCrudContext, entity: TModel) -> None:
        context.session.delete(entity)
        context.session.flush()

    def delete_by_id(self, context: SqlAlchemyCrudContext, id: ID) -> None:
        entity = self.find_by_id(context, id)
        if entity is not None:
            self.delete(context, entity)

    def delete_all(self, context: SqlAlchemyCrudContext) -> None:
        context.session.execute(sql_delete(self._model_class))
        context.session.flush()

    def delete_all_by_id(self, context: SqlAlchemyCrudContext, ids: Iterable[ID]) -> None:
        ids = list(ids)
        context.session.execute(sql_delete(self._model_class).where(self._id_column.in_(ids)))
        context.session.flush()
