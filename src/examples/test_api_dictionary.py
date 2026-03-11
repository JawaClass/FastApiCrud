from fastapi import Depends, FastAPI
from pydantic import Field
from src.api.api import ApiBuilder, FilterString, FilterDependency
from src.service.crud_service_mapper import NoOpCrudServiceMapper
from src.service.dictionary_crud_service import DictionaryCrudService, DictionaryCrudContext
from src.repository.dictionary_crud_repository import DictionaryCrudRepository, DictionaryFilter
from typing import Any, Callable
import uuid


def test_build_api():

    MyDictRepo = DictionaryCrudRepository[dict[str, Any], int]
    repo = MyDictRepo(id_field="id", id_generator=lambda: uuid.uuid1().int)

    class MyMapper(NoOpCrudServiceMapper[dict[str, Any]]):
        def update_entity(
            self, entity: dict[str, Any], update_dto: dict[str, Any]
        ) -> dict[str, Any]:
            return {
                **entity,
                **update_dto,
            }

    mapper = MyMapper()
    service = DictionaryCrudService(repository=repo, mapper=mapper)

    class MFilter(FilterString):
        name_eq: str | None = Field(default=None)
        name_startswith: str | None = Field(default=None)
        name_in: str | None = Field(default=None)

    def filter_factory(url_filter: MFilter) -> DictionaryFilter[dict[str, Any]]:
        assert isinstance(url_filter, MFilter)

        class MyDictionaryFilter(DictionaryFilter[dict[str, Any]]):
            def apply(self, target: list[dict[str, Any]]) -> list[dict[str, Any]]:

                name_in: list[str] = []
                predciates: list[Callable[[dict[str, Any]], bool]] = []

                if url_filter.name_in:
                    name_in = [n.strip() for n in url_filter.name_in.split(",")]
                    predciates.append(lambda entity: entity.get("name") in name_in)

                return [x for x in target if all(pred(x) for pred in predciates)]

        return MyDictionaryFilter()

    api = ApiBuilder(
        service=service,
        prefix="/pokemon",
        response_cls=dict[str, Any],
        context_resolver=lambda: DictionaryCrudContext(),
    )

    return api.with_all(
        create_cls=dict,
        id_cls=int,
        update_cls=dict,
        filter_by_dep=FilterDependency(type_=MFilter, depends_=Depends()),
        filter_factory=filter_factory,
    ).build()


x = test_build_api()

ctx = DictionaryCrudContext()

x.service.create_all(
    ctx,
    [
        {"name": "Pikachu"},
        {"name": "Glumanda"},
        {"name": "Bisasam"},
        {"name": "Schiggy"},
        {"name": "Zubat"},
    ],
)

# print("ALL", x.service.get_all(ctx))

# uv run -m fastapi dev --entrypoint src.api.test_api:app
app = FastAPI()

app.include_router(x.fastapi_router)
