from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Iterable, Generic

from typing_extensions import TypeVar

from src.repository.crud_filter import Filter


TModel = TypeVar("TModel")
ID = TypeVar("ID")
F = TypeVar("F", bound=Filter[Any])
TContext = TypeVar("TContext")


class CrudRepository(ABC, Generic[TModel, ID, F, TContext]):
    @abstractmethod
    def count(self, context: TContext, filters: F | None = None) -> int:
        pass

    @abstractmethod
    def save(self, context: TContext, entity: TModel) -> TModel:
        pass

    @abstractmethod
    def save_all(self, context: TContext, entities: Iterable[TModel]) -> Iterable[TModel]:
        pass

    @abstractmethod
    def find_by_id(self, context: TContext, id: ID) -> TModel | None:
        pass

    @abstractmethod
    def exists_by_id(self, context: TContext, id: ID) -> bool:
        pass

    @abstractmethod
    def find_all(self, context: TContext, filters: F | None = None) -> Iterable[TModel]:
        pass

    @abstractmethod
    def find_all_by_id(self, context: TContext, ids: Iterable[ID]) -> Iterable[TModel]:
        pass

    @abstractmethod
    def delete(self, context: TContext, entity: TModel) -> None:
        pass

    @abstractmethod
    def delete_by_id(self, context: TContext, id: ID) -> None:
        pass

    @abstractmethod
    def delete_all(self, context: TContext) -> None:
        pass

    @abstractmethod
    def delete_all_by_id(self, context: TContext, ids: Iterable[ID]) -> None:
        pass
