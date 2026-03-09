from __future__ import annotations
from typing import Generic

from typing_extensions import TypeVar
from src.repository.dictionary_crud_repository import (
    DictionaryCrudContext,
    DictionaryCrudRepository,
    DictionaryFilter,
)
from src.service.crud_service_mapper import CrudServiceMapper
from src.service.crud_service import CrudService
from src.repository.dictionary_crud_repository import TModel

TCreate = TypeVar("TCreate")
TUpdate = TypeVar("TUpdate")
TResponse = TypeVar("TResponse")
ID = TypeVar("ID")


class DictionaryCrudService(
    Generic[TModel, TCreate, TUpdate, TResponse, ID],
    CrudService[
        TModel, TCreate, TUpdate, TResponse, ID, DictionaryFilter[TModel], DictionaryCrudContext
    ],
):
    def __init__(
        self,
        repository: DictionaryCrudRepository[TModel, ID],
        mapper: CrudServiceMapper[TModel, TCreate, TUpdate, TResponse],
    ):
        self._repository = repository
        self._mapper = mapper

    def create(self, context: DictionaryCrudContext, data: TCreate) -> TResponse:
        entity = self._mapper.to_entity(data)
        saved = self._repository.save(context, entity)
        return self._mapper.to_response(saved)

    def create_all(self, context: DictionaryCrudContext, data: list[TCreate]) -> list[TResponse]:
        entities = [self._mapper.to_entity(d) for d in data]
        saved = self._repository.save_all(context, entities)
        return [self._mapper.to_response(e) for e in saved]

    def get_by_id(self, context: DictionaryCrudContext, id: ID) -> TResponse | None:
        entity = self._repository.find_by_id(context, id)
        if entity is None:
            return None
        return self._mapper.to_response(entity)

    def exists_by_id(self, context: DictionaryCrudContext, id: ID) -> bool:
        return self._repository.exists_by_id(context, id)

    def get_all(
        self, context: DictionaryCrudContext, filters: DictionaryFilter[TModel] | None = None
    ) -> list[TResponse]:
        entities = self._repository.find_all(context, filters)
        return [self._mapper.to_response(e) for e in entities]

    def get_all_by_id(self, context: DictionaryCrudContext, ids: list[ID]) -> list[TResponse]:
        entities = self._repository.find_all_by_id(context, ids)
        return [self._mapper.to_response(e) for e in entities]

    def count(
        self, context: DictionaryCrudContext, filters: DictionaryFilter[TModel] | None = None
    ) -> int:
        return self._repository.count(context, filters)

    def update(self, context: DictionaryCrudContext, id: ID, data: TUpdate) -> TResponse | None:
        entity = self._repository.find_by_id(context, id)
        if entity is None:
            return None
        updated = self._mapper.update_entity(entity, data)
        saved = self._repository.save(context, updated)
        return self._mapper.to_response(saved)

    def delete(self, context: DictionaryCrudContext, id: ID) -> None:
        entity = self._repository.find_by_id(context, id)
        if entity is not None:
            self._repository.delete(context, entity)

    def delete_by_id(self, context: DictionaryCrudContext, id: ID) -> None:
        self._repository.delete_by_id(context, id)

    def delete_all(self, context: DictionaryCrudContext) -> None:
        self._repository.delete_all(context)

    def delete_all_by_id(self, context: DictionaryCrudContext, ids: list[ID]) -> None:
        self._repository.delete_all_by_id(context, ids)
