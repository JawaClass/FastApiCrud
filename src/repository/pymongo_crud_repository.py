from __future__ import annotations
from typing import Any, Iterable, TypeVar, cast, Generic
from pymongo.collection import Collection
from src.repository.crud_repository import CrudRepository
from src.repository.mongo_filter import MongoFilter
from dataclasses import dataclass

TModel = TypeVar("TModel", bound=dict[str, Any])
TID = TypeVar("TID")

NoneValue = object()


@dataclass(frozen=True)
class PyMongoCrudContext(Generic[TModel]):
    collection: Collection[TModel]


class PyMongoCrudRepository(CrudRepository[TModel, TID, MongoFilter, PyMongoCrudContext[TModel]]):
    _id_name = "_id"

    def count(self, context: PyMongoCrudContext[TModel], filters: MongoFilter | None = None) -> int:
        query: dict[str, Any] = {}
        if filters:
            query = filters.apply(query)
        return context.collection.count_documents(query)

    def save(self, context: PyMongoCrudContext[TModel], entity: TModel) -> TModel:
        result = context.collection.replace_one(
            {self._id_name: entity.get(self._id_name)}, entity, upsert=True
        )
        result_entity = {**entity}
        if result.upserted_id is not None:
            result_entity[self._id_name] = result.upserted_id
        return cast(TModel, result_entity)

    def save_all(
        self, context: PyMongoCrudContext[TModel], entities: Iterable[TModel]
    ) -> Iterable[TModel]:
        return [self.save(context, entity) for entity in entities]

    def find_by_id(self, context: PyMongoCrudContext[TModel], id: TID) -> TModel | None:
        result = context.collection.find_one({self._id_name: id})
        return result

    def exists_by_id(self, context: PyMongoCrudContext[TModel], id: TID) -> bool:
        return context.collection.count_documents({self._id_name: id}) > 0

    def find_all(
        self, context: PyMongoCrudContext[TModel], filters: MongoFilter | None = None
    ) -> Iterable[TModel]:
        query: dict[str, Any] = {}
        if filters:
            query = filters.apply(query)
        cursor = context.collection.find(query)
        return (entity for entity in cursor)

    def find_all_by_id(
        self, context: PyMongoCrudContext[TModel], ids: Iterable[TID]
    ) -> Iterable[TModel]:
        cursor = context.collection.find({self._id_name: {"$in": ids}})
        return (entity for entity in cursor)

    def delete(self, context: PyMongoCrudContext[TModel], entity: TModel) -> None:
        id = entity.get(self._id_name, NoneValue)
        if id is NoneValue:
            return None
        id = cast(TID, id)
        self.delete_by_id(context, id)

    def delete_by_id(self, context: PyMongoCrudContext[TModel], id: TID) -> None:
        context.collection.delete_one({self._id_name: id})

    def delete_all(self, context: PyMongoCrudContext[TModel]) -> None:
        context.collection.delete_many({})

    def delete_all_by_id(self, context: PyMongoCrudContext[TModel], ids: Iterable[TID]) -> None:
        context.collection.delete_many({self._id_name: {"$in": ids}})
