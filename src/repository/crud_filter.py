from __future__ import annotations
from abc import abstractmethod, ABC
from dataclasses import dataclass, field
from typing import Any, cast

# from typing import  List, Sequence, TypeVar
from sqlalchemy import ColumnElement, Select


class Filter[E](ABC):
    @abstractmethod
    def apply(self, target: E) -> E:
        pass


class StrFilter(Filter[str]):
    def apply(self, target: str) -> str:
        return target


@dataclass
class SaFilter[E](Filter[Select[tuple[E]]]):
    def apply(self, target: Select[tuple[E]]) -> Select[tuple[E]]:
        return target


@dataclass
class SaFilterImpl[E](SaFilter[E]):
    conditions: list[ColumnElement[bool]] = field(default_factory=list[ColumnElement[bool]])
    order_by: list[Any] | Any | None = None
    limit: int | None = None
    offset: int | None = None
    options: tuple[Any, ...] = field(default_factory=tuple)

    def apply(self, target: Select[tuple[E]]) -> Select[tuple[E]]:

        for condition in self.conditions:
            target = target.where(condition)

        if self.order_by is not None:
            if isinstance(self.order_by, (list, tuple)):
                order_by = cast(list[Any], self.order_by)  # type: ignore
                target = target.order_by(*order_by)
            else:
                target = target.order_by(self.order_by)

        if self.limit is not None:
            target = target.limit(self.limit)
        if self.offset is not None:
            target = target.offset(self.offset)
        if self.options:
            target = target.options(*self.options)

        return target
