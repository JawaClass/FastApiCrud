print("aaaaaa")

from fastapi import Depends, FastAPI
from pydantic import BaseModel
from src.api.api import UrlParamDependency
from src.repository.sqlalchemy_crud_repository import SqlAlchemyCrudContext
from typing import List, Optional
from sqlalchemy import String, ForeignKey, Integer, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, sessionmaker
from fastapi_filters import (
    FilterField,
    FilterSet,
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

print("heyyyyyyyyyyyyyyyyyyyyyyyyy")
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

 

filtering_call = create_filters_from_model(TrainerResponse)
sorting_call = create_sorting_from_model(TrainerResponse)
class MyCustomUrlFilter:
    
    def __init__(
        self,
        pagination: SaFilterOffsetPagination = Depends(SaFilterOffsetPagination),
        filtering=Depends(filtering_call), # type: ignore
        sorting=Depends(sorting_call) # type: ignore
    ):
        self.pagination = pagination
        self.filtering = filtering
        self.sorting = sorting

def build_filter_factory(url_params: MyCustomUrlFilter):
    """
    resolve the dependencies and create SaFilters from it...
    """  
    assert isinstance(url_params, MyCustomUrlFilter) 

    sa_filter = SaFilterFilterSet(filters=url_params.filtering)
    sa_sort = SaFilterSortingValues(sorting=url_params.sorting)
    sa_page = url_params.pagination

    return FastApiFiltersSortOffsetPagingSaFilter(
        filterring=sa_filter,
        sorting=sa_sort,
        pagination=sa_page
    )

my_api = build_sa_api(
    prefix="/trainer",
    model_cls=Trainer,
    create_cls=TrainerCreate,
    response_cls=TrainerResponse,
    update_cls=TrainerUpdate,
    session_maker=new_session,
    id_column=Trainer.id,
    filter_factory=build_filter_factory,
    filter_params=UrlParamDependency(MyCustomUrlFilter, MyCustomUrlFilter)
)

ctx = SqlAlchemyCrudContext(new_session())

my_api.service.create_all(
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

# uv run -m fastapi dev --entrypoint src.examples.sa:app
app = FastAPI()

app.include_router(my_api.fastapi_router) 