# from __future__ import annotations
# from typing import Any

# from sqlalchemy.orm import Session

# from src.service.crud_service_mapper import CrudServiceMapper
# from src.repository import SqlAlchemyCrudRepository
# from src.service import SqlAlchemyCrudService
# from .conftest import User

# type UserDict = dict[str, Any]


# class Mapper(CrudServiceMapper[User, UserDict, UserDict, User]):
#     def to_entity(self, create_dto: UserDict) -> User:
#         return User(
#             id=create_dto.get("id"),
#             name=create_dto.get("name"),
#             email=create_dto.get("email"),
#         )

#     # def to_response(self, entity: User) -> UserDict:
#     #     return {
#     #         "id": entity.id,
#     #         "name": entity.name,
#     #         "email": entity.email,
#     #     }

#     def update_entity(self, entity: User, update_dto: UserDict) -> User:
#         return User(
#             id=update_dto.get("id", entity.id),
#             name=update_dto.get("name", entity.name),
#             email=update_dto.get("email", entity.email),
#         )

#     def to_response(self, entity: User) -> User:
#         return entity


# def test_service(session: Session):

#     repo = SqlAlchemyCrudRepository(model_class=User, id_column=User.id)

#     service = SqlAlchemyCrudService(repository=repo, mapper=Mapper())

#     _ = service.count(session=session)

#     _ = service.create(session=session, data={"name": "hahha", "email": "hahha2"})


# # uv run -m pytest tests/test_service_types.py
