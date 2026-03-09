from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any

from src.repository.crud_filter import Filter

type MongoQuery = dict[str, Any]


@dataclass
class MongoFilter(Filter[MongoQuery]):
    query: dict[str, Any] = field(default_factory=dict[str, Any])
    sort: list[tuple[str, int]] | None = None
    limit: int | None = None
    skip: int | None = None
    projection: dict[str, Any] | None = None

    def apply(self, target: dict[str, Any] | None = None) -> dict[str, Any]:
        return self.query

    def to_find_options(self) -> dict[str, Any]:
        options: dict[str, Any] = {}
        if self.sort:
            options["sort"] = self.sort
        if self.limit is not None:
            options["limit"] = self.limit
        if self.skip is not None:
            options["skip"] = self.skip
        if self.projection:
            options["projection"] = self.projection
        return options

    @classmethod
    def eq(cls, field: str, value: Any) -> MongoFilter:
        return cls(query={field: value})

    @classmethod
    def ne(cls, field: str, value: Any) -> MongoFilter:
        return cls(query={field: {"$ne": value}})

    @classmethod
    def gt(cls, field: str, value: Any) -> MongoFilter:
        return cls(query={field: {"$gt": value}})

    @classmethod
    def gte(cls, field: str, value: Any) -> MongoFilter:
        return cls(query={field: {"$gte": value}})

    @classmethod
    def lt(cls, field: str, value: Any) -> MongoFilter:
        return cls(query={field: {"$lt": value}})

    @classmethod
    def lte(cls, field: str, value: Any) -> MongoFilter:
        return cls(query={field: {"$lte": value}})

    @classmethod
    def in_list(cls, field: str, values: list[Any]) -> MongoFilter:
        return cls(query={field: {"$in": values}})

    @classmethod
    def nin(cls, field: str, values: list[Any]) -> MongoFilter:
        return cls(query={field: {"$nin": values}})

    @classmethod
    def regex(cls, field: str, pattern: str, options: str = "") -> MongoFilter:
        return cls(query={field: {"$regex": pattern, "$options": options}})

    @classmethod
    def and_filter(cls, *filters: MongoFilter) -> MongoFilter:
        queries = [f.query for f in filters]
        return cls(query={"$and": queries})

    @classmethod
    def or_filter(cls, *filters: MongoFilter) -> MongoFilter:
        queries = [f.query for f in filters]
        return cls(query={"$or": queries})

    @classmethod
    def nor(cls, *filters: MongoFilter) -> MongoFilter:
        queries = [f.query for f in filters]
        return cls(query={"$nor": queries})

    @classmethod
    def not_filter(cls, filter_obj: MongoFilter) -> MongoFilter:
        return cls(query={"$not": filter_obj.query})
