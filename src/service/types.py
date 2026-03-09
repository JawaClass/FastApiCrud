from __future__ import annotations
from typing import Any

from typing_extensions import TypeVar

from ..repository.crud_filter import Filter


# generic typevars for alle repos or services
TModel = TypeVar("TModel", bound=Any)
TCreate = TypeVar("TCreate")
TUpdate = TypeVar("TUpdate")
TResponse = TypeVar("TResponse")
TID = TypeVar("TID")
TContext = TypeVar("TContext", bound=Any)
TFilter = TypeVar("TFilter", bound=Filter[Any])
