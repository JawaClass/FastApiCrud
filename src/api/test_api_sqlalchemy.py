from fastapi import FastAPI
from pydantic import BaseModel
from src.repository.crud_filter import SaFilter
from src.api.api import UrlParamDependency
from src.repository.sqlalchemy_crud_repository import SqlAlchemyCrudContext
from typing import Any, Callable, List, Optional
from sqlalchemy import String, ForeignKey, Integer, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, sessionmaker
from fastapi_filters import (
    FilterField,
    FilterSet,
    SortingValues,
    create_filters_from_model,
    create_sorting_from_model,
)

from src.api.api_builders.sqlalchemy_api_builder import build_api as build_sa_api
from src.api.filter_factories.fastapi_filters_factory import (
    FastApiFiltersSortOffsetPagingSaFilter,
    SaFilterFilterSet,
    SaFilterOffsetPagination,
    SaFilterSortingValues,
)


# 1. Define a Base class for all models
class Base(DeclarativeBase):
    pass


# 2. The Trainer class (The "One" in One-to-Many)
class Trainer(Base):
    __tablename__ = "trainer"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    region: Mapped[Optional[str]] = mapped_column(String(30))

    # Relationship to the Pokemon class
    # 'back_populates' keeps both sides of the relationship in sync
    pokemons: Mapped[List["Pokemon"]] = relationship(
        back_populates="owner", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"Trainer(id={self.id!r}, name={self.name!r})"


# 3. The Pokemon class (The "Many" in One-to-Many)
class Pokemon(Base):
    __tablename__ = "pokemon"

    id: Mapped[int] = mapped_column(primary_key=True)
    species: Mapped[str] = mapped_column(String(50), nullable=False)
    level: Mapped[int] = mapped_column(Integer, default=1)
    poke_type: Mapped[str] = mapped_column(String(20))

    # Foreign Key to the Trainer
    trainer_id: Mapped[Optional[int]] = mapped_column(ForeignKey("trainer.id"))

    # Relationship back to the Trainer
    owner: Mapped[Optional["Trainer"]] = relationship(back_populates="pokemons")


eng = create_engine("sqlite:///:memory:")
Base.metadata.create_all(eng)
new_session = sessionmaker(bind=eng)


class TrainerWithoutId(BaseModel):
    name: str
    region: str | None = None


class TrainerCreate(TrainerWithoutId):
    pass


class TrainerUpdate(TrainerWithoutId):
    pass


class TrainerResponse(TrainerWithoutId):
    id: int


class TrainerFilters(FilterSet):
    name: FilterField[str]


def prepare_filter_dependency(
    dependency: Callable[..., Any], filter_factory: Callable[[Any], SaFilter[Any]]
):
    """
    Example:
        filter_resolver = create_filters_from_model(TrainerResponse)
        prepare_filter_dependency(filter_resolver)
    """
    print("prepare_filter_dependency...", dependency)
    import inspect

    sig = inspect.signature(dependency)

    async def my_filter(*args: Any, **kwargs: Any) -> SaFilter[Any]:
        resolved_dependency = await dependency(*args, **kwargs)
        filter_ = filter_factory(resolved_dependency)
        assert isinstance(filter_, SaFilter)
        return filter_

    # 3. Apply the signature hijack
    my_filter.__signature__ = sig  # type: ignore
    # Optional: ensure metadata like __name__ matches for cleaner debugging
    my_filter.__name__ = dependency.__name__  # type: ignore

    return my_filter


x = build_sa_api(
    prefix="/trainer",
    model_cls=Trainer,
    create_cls=TrainerCreate,
    response_cls=TrainerResponse,
    update_cls=TrainerUpdate,
    session_maker=new_session,
    id_column=Trainer.id,
    id_cls=int,
    filter_factory=lambda ctx: FastApiFiltersSortOffsetPagingSaFilter(
        filterring=ctx.url_filter, sorting=ctx.url_sorting, pagination=ctx.url_pagination
    ),
    filter_dependency=UrlParamDependency(
        type_=SaFilterFilterSet,
        depends_=prepare_filter_dependency(
            dependency=create_filters_from_model(TrainerResponse),
            filter_factory=lambda resolved_filter: SaFilterFilterSet(filters=resolved_filter),
        ),
    ),
    sorting_dependency=UrlParamDependency(
        type_=SortingValues,
        depends_=prepare_filter_dependency(
            dependency=create_sorting_from_model(TrainerResponse),
            filter_factory=lambda resolved_filter: SaFilterSortingValues(sorting=resolved_filter),
        ),
    ),
    pagination_dependency=UrlParamDependency(
        type_=SaFilterOffsetPagination,
    ),
)

ctx = SqlAlchemyCrudContext(new_session())

x.service.create_all(
    ctx,
    [
        TrainerCreate(name="Ash Ketchum", region="Kanto"),
        TrainerCreate(name="Misty", region="Kanto"),
        TrainerCreate(name="Brock", region="Kanto"),
        TrainerCreate(name="Cynthia", region="Sinnoh"),
        TrainerCreate(name="Steven Stone", region="Hoenn"),
        TrainerCreate(name="Lance", region="Johto"),
        TrainerCreate(name="Leon", region="Galar"),
        TrainerCreate(name="Red", region="Kanto"),
        TrainerCreate(name="Blue", region="Kanto"),
        TrainerCreate(name="N", region="Unova"),
    ],
)

# uv run -m fastapi dev --entrypoint src.api.test_api_sqlalchemy:app
app = FastAPI()

app.include_router(x.fastapi_router)
