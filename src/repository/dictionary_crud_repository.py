from __future__ import annotations

from typing import Any, Iterable, TypeVar
from src.repository.crud_filter import Filter
from src.repository.crud_repository import CrudRepository
from typing import Generic, Callable
from dataclasses import dataclass, field


TModel = TypeVar("TModel", bound=dict[str, Any])
ID = TypeVar("ID")
F = TypeVar("F", bound=Filter[Any])

NoIdAvailable = object()


@dataclass(frozen=True)
class DictionaryCrudContext:
    pass


@dataclass(frozen=True)
class Sort:
    asc: list[str] | None = None
    desc: list[str] | None = None


@dataclass
class DictionaryFilter(Filter[list[TModel]]):
    field_eq: list[tuple[str, Any]] = field(default_factory=lambda: [])

    def _keep(self, entity: TModel) -> bool:
        return all(entity.get(k) == v for k, v in self.field_eq)

    def apply(self, target: list[TModel]) -> list[TModel]:
        return [e for e in target if self._keep(e)]


class DictionaryCrudRepository(
    Generic[TModel, ID], CrudRepository[TModel, ID, DictionaryFilter[TModel], DictionaryCrudContext]
):
    def __init__(self, id_field: str, id_generator: Callable[[], ID]) -> None:
        super().__init__()
        self.dictionary: dict[ID, Any] = {}
        self.id_field = id_field
        self.id_generator = id_generator

    def save(self, context: DictionaryCrudContext, entity: TModel) -> TModel:
        id = entity.get(self.id_field, NoIdAvailable)

        if id is NoIdAvailable:
            id = self.id_generator()
            print("id...", id)
            entity[self.id_field] = id

        self.dictionary[id] = entity
        return entity

    def save_all(
        self, context: DictionaryCrudContext, entities: Iterable[TModel]
    ) -> Iterable[TModel]:
        return [self.save(context, entity) for entity in entities]

    def find_by_id(self, context: DictionaryCrudContext, id: ID) -> TModel | None:
        return self.dictionary.get(id)

    def exists_by_id(self, context: DictionaryCrudContext, id: ID) -> bool:
        return self.find_by_id(context, id) is not None

    def find_all(
        self, context: DictionaryCrudContext, filters: DictionaryFilter[TModel] | None = None
    ) -> Iterable[TModel]:
        entities = list(self.dictionary.values())
        if filters:
            entities = filters.apply(entities)
        return entities

    def find_all_by_id(self, context: DictionaryCrudContext, ids: Iterable[ID]) -> Iterable[TModel]:
        raise NotImplementedError()

    def count(
        self, context: DictionaryCrudContext, filters: DictionaryFilter[TModel] | None = None
    ) -> int:
        raise NotImplementedError()

    def delete(self, context: DictionaryCrudContext, entity: TModel) -> None:
        id = entity.get(self.id_field)
        if id is None:
            return
        self.delete_by_id(context, id)

    def delete_by_id(self, context: DictionaryCrudContext, id: ID) -> None:
        entity = self.find_by_id(context, id)
        if entity is not None:
            self.delete(context, entity)

    def delete_all(self, context: DictionaryCrudContext) -> None:
        self.dictionary = {}

    def delete_all_by_id(self, context: DictionaryCrudContext, ids: Iterable[ID]) -> None:
        for id in ids:
            self.delete_by_id(context, id)
