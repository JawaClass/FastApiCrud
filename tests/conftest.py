from __future__ import annotations
from dataclasses import dataclass
from typing import Callable, Generator, Any

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import (
    Mapped,
    Session,
    declarative_base,
    mapped_column,
    sessionmaker,
)

from src.repository import SqlAlchemyCrudRepository

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    email: Mapped[str]


@dataclass
class CreateUserRequest:
    name: str
    email: str


@dataclass
class UpdateUserRequest:
    name: str
    email: str


@dataclass
class UserResponse:
    id: int
    name: str
    email: str


@pytest.fixture
def engine() -> Generator[Any, None, None]:
    eng = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(eng)
    yield eng


@pytest.fixture
def session_factory(engine: Any) -> sessionmaker[Session]:
    return sessionmaker(bind=engine)


@pytest.fixture
def session(session_factory: sessionmaker[Session]) -> Generator[Session, None, None]:
    with session_factory() as s:
        yield s


@pytest.fixture
def repository() -> SqlAlchemyCrudRepository[User, int]:
    return SqlAlchemyCrudRepository(User, User.id)  # type: ignore[arg-type]


@pytest.fixture
def to_entity() -> Callable[[CreateUserRequest], User]:
    def _to_entity(data: CreateUserRequest) -> User:
        return User(name=data.name, email=data.email)

    return _to_entity


@pytest.fixture
def to_response() -> Callable[[User], UserResponse]:
    def _to_response(entity: User) -> UserResponse:
        return UserResponse(id=entity.id, name=entity.name, email=entity.email)

    return _to_response


@pytest.fixture
def update_entity() -> Callable[[User, UpdateUserRequest], User]:
    def _update_entity(entity: User, data: UpdateUserRequest) -> User:
        entity.name = data.name
        entity.email = data.email
        return entity

    return _update_entity
