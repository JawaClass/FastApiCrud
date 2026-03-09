from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Generic
from src.service.types import TModel, TCreate, TResponse, TUpdate, TFilter, TID, TContext


class CrudService(ABC, Generic[TModel, TCreate, TUpdate, TResponse, TID, TFilter, TContext]):
    @abstractmethod
    def create(self, context: TContext, data: TCreate) -> TResponse:
        pass

    @abstractmethod
    def create_all(self, context: TContext, data: list[TCreate]) -> list[TResponse]:
        pass

    @abstractmethod
    def get_by_id(self, context: TContext, id: TID) -> TResponse | None:
        pass

    @abstractmethod
    def exists_by_id(self, context: TContext, id: TID) -> bool:
        pass

    @abstractmethod
    def get_all(self, context: TContext, filters: TFilter | None = None) -> list[TResponse]:
        pass

    @abstractmethod
    def get_all_by_id(self, context: TContext, ids: list[TID]) -> list[TResponse]:
        pass

    @abstractmethod
    def count(self, context: TContext, filters: TFilter | None = None) -> int:
        pass

    @abstractmethod
    def update(self, context: TContext, id: TID, data: TUpdate) -> TResponse | None:
        pass

    @abstractmethod
    def delete(self, context: TContext, id: TID) -> None:
        pass

    @abstractmethod
    def delete_by_id(self, context: TContext, id: TID) -> None:
        pass

    @abstractmethod
    def delete_all(self, context: TContext) -> None:
        pass

    @abstractmethod
    def delete_all_by_id(self, context: TContext, ids: list[TID]) -> None:
        pass
