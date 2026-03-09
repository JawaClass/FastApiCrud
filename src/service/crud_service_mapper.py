from pydantic import BaseModel
from sqlalchemy.orm import DeclarativeBase

from src.service.types import TModel, TCreate, TUpdate, TResponse
from abc import ABC, abstractmethod
from typing import Generic


class CrudServiceMapper(ABC, Generic[TModel, TCreate, TUpdate, TResponse]):
    @abstractmethod
    def to_entity(self, create_dto: TCreate) -> TModel:
        pass

    @abstractmethod
    def to_response(self, entity: TModel) -> TResponse:
        pass

    @abstractmethod
    def update_entity(self, entity: TModel, update_dto: TUpdate) -> TModel:
        pass


class NoOpCrudServiceMapper(CrudServiceMapper[TModel, TModel, TModel, TModel]):
    def to_entity(self, create_dto: TModel) -> TModel:
        return create_dto

    def to_response(self, entity: TModel) -> TModel:
        return entity

    def update_entity(self, entity: TModel, update_dto: TModel) -> TModel:
        return update_dto


class SqlAlchemyAutoMapper[
    TModel: DeclarativeBase,
    TCreate: BaseModel,
    TUpdate: BaseModel,
    TResponse: BaseModel,
](CrudServiceMapper[TModel, TCreate, TUpdate, TResponse]):
    def __init__(
        self,
        model_cls: type[TModel],
        response_cls: type[TResponse],
        create_cls: type[TCreate],
        update_cls: type[TUpdate],
    ):
        self.model_cls = model_cls
        self.response_cls = response_cls

    # @staticmethod
    # def create(
    #     model_cls: type[TModel],
    #     create_cls: type[TCreate],
    #     update_cls: type[TUpdate],
    #     response_cls: type[TResponse],
    # ):
    #     return SqlAlchemyAutoMapper[TModel, TCreate, TUpdate, TResponse](model_cls=model_cls, response_cls=response_cls)

    def to_entity(self, create_dto: TCreate) -> TModel:
        """Instantiates the SA Model with data from the Create DTO."""
        print("SqlAlchemyAutoMapper::to_entity", create_dto)
        return self.model_cls(**create_dto.model_dump())

    def to_response(self, entity: TModel) -> TResponse:
        """
        Maps the SA Model to a Response DTO.
        Works best if the DTO has 'from_attributes=True' (Pydantic v2).
        """
        if all(
            [
                hasattr(self.response_cls, "model_validate"),
                hasattr(self.response_cls, "model_config"),
            ]
        ):
            # Pydantic v2 standard for ORM objects
            if model_config := getattr(self.response_cls, "model_config"):
                if isinstance(model_config, dict):
                    if model_config.get("from_attributes"):  # type: ignore
                        return self.response_cls.model_validate(entity)

        # Fallback for manual mapping if from_attributes isn't used
        data = {
            field: getattr(entity, field)
            for field in self.response_cls.model_fields
            if hasattr(entity, field)
        }
        return self.response_cls(**data)

    def update_entity(self, entity: TModel, update_dto: TUpdate) -> TModel:
        """Updates only the fields provided in the Update DTO."""
        update_data = update_dto.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            if hasattr(entity, key):
                setattr(entity, key, value)
        return entity
