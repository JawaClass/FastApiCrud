from dataclasses import field, dataclass
from typing import Any

from fastapi_filters import FilterSet, FilterValues, SortingValues
from fastapi_filters.ext.sqlalchemy import apply_filters, apply_sorting

from src.repository.crud_filter import SaFilter
from sqlalchemy import Select
from .base import FilterSortPagingSaFilter
from sqlalchemy.orm import InstrumentedAttribute


@dataclass
class SaFilterFilterSet(SaFilter[Any]):
    filters: FilterValues | FilterSet

    def apply(self, target: Select[tuple[Any]]) -> Select[tuple[Any]]:
        return apply_filters(stmt=target, filters=self.filters)


@dataclass
class SaFilterSortingValues(SaFilter[Any]):
    sorting: SortingValues

    def apply(self, target: Select[tuple[Any]]) -> Select[tuple[Any]]:
        return apply_sorting(stmt=target, sorting=self.sorting)


@dataclass
class SaFilterOffsetPagination(SaFilter[Any]):
    offset: int | None = field(default=None)
    limit: int | None = field(default=None)

    def apply(self, target: Select[tuple[Any]]) -> Select[tuple[Any]]:
        return target.limit(self.limit).offset(self.offset)


def SaCursorPagination(id_column: InstrumentedAttribute[Any]):
    """
    Factory function because id_column is required to perform pagination.
    That way we can use our class as FastAPI Dependeny
    """

    @dataclass
    class SaCursorPagination(SaFilter[Any]):
        cursor: int | None = field(default=None)
        limit: int | None = field(default=None)

        def apply(self, target: Select[tuple[Any]]) -> Select[tuple[Any]]:
            if self.cursor is not None:
                target = target.where(id_column > self.cursor)
            return target.limit(self.limit)

    return SaCursorPagination


@dataclass
class SaPagePagination(SaFilter[Any]):
    page: int = field(default=1)
    page_size: int = field(default=20)

    def apply(self, target: Select[tuple[Any]]) -> Select[tuple[Any]]:
        return target.limit(self.page_size).offset((self.page - 1) * self.page_size)


# for automatic type checking at instantiaton time
from pydantic.dataclasses import dataclass as pydantic_dataclass  # noqa: E402


@pydantic_dataclass
class FastApiFiltersSortOffsetPagingSaFilter(
    FilterSortPagingSaFilter[SaFilterFilterSet, SaFilterSortingValues, SaFilterOffsetPagination]
):
    filterring: SaFilterFilterSet | None = None
    sorting: SaFilterSortingValues | None = None
    pagination: SaFilterOffsetPagination | None = None
