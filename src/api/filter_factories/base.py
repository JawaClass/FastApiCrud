from typing import Any, TypeVar, Generic
from src.repository.crud_filter import SaFilter
from sqlalchemy import Select

T_Filter = TypeVar("T_Filter", bound=SaFilter[Any])
T_Sort = TypeVar("T_Sort", bound=SaFilter[Any])
T_Page = TypeVar("T_Page", bound=SaFilter[Any])


class FilterSortPagingSaFilter(Generic[T_Filter, T_Sort, T_Page], SaFilter[Any]):
    filterring: T_Filter | None = None
    sorting: T_Sort | None = None
    pagination: T_Page | None = None

    def apply(self, target: Select[tuple[Any]]) -> Select[tuple[Any]]:

        print("type filterring", type(self.filterring))
        print("type sorting", type(self.sorting), self.sorting)
        print("type pagination", type(self.pagination))

        if self.filterring:
            target = self.filterring.apply(target)
        if self.sorting:
            target = self.sorting.apply(target)
        if self.pagination:
            target = self.pagination.apply(target)

        return target
