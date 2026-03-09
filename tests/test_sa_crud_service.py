# from __future__ import annotations
# from typing import Callable
# import pytest
# from sqlalchemy.orm import Session

# from src.repository import SaFilter, SqlAlchemyCrudRepository
# from src.service import SqlAlchemyCrudService
# from .conftest import (
#     User,
#     CreateUserRequest,
#     UpdateUserRequest,
#     UserResponse,
# )


# @pytest.fixture
# def service(
#     repository: SqlAlchemyCrudRepository[User, int],
#     to_entity: Callable[[CreateUserRequest], User],
#     to_response: Callable[[User], UserResponse],
#     update_entity: Callable[[User, UpdateUserRequest], User],
# ) -> SqlAlchemyCrudService[User, CreateUserRequest, UpdateUserRequest, UserResponse, int]:
#     return SqlAlchemyCrudService(
#         repository=repository,
#         to_entity=to_entity,
#         to_response=to_response,
#         update_entity=update_entity,
#     )


# class TestCreate:
#     def test_create_returns_response(
#         self,
#         service: SqlAlchemyCrudService[
#             User, CreateUserRequest, UpdateUserRequest, UserResponse, int
#         ],
#         session: Session,
#     ) -> None:
#         result = service.create(session, CreateUserRequest(name="John", email="john@test.com"))
#         assert isinstance(result, UserResponse)
#         assert result.name == "John"
#         assert result.email == "john@test.com"
#         assert result.id == 1

#     def test_create_persists_entity(
#         self,
#         service: SqlAlchemyCrudService[
#             User, CreateUserRequest, UpdateUserRequest, UserResponse, int
#         ],
#         session: Session,
#     ) -> None:
#         service.create(session, CreateUserRequest(name="John", email="john@test.com"))
#         users = session.query(User).all()
#         assert len(users) == 1
#         assert users[0].name == "John"


# class TestCreateAll:
#     def test_create_all_returns_responses(
#         self,
#         service: SqlAlchemyCrudService[
#             User, CreateUserRequest, UpdateUserRequest, UserResponse, int
#         ],
#         session: Session,
#     ) -> None:
#         data = [
#             CreateUserRequest(name="John", email="john@test.com"),
#             CreateUserRequest(name="Jane", email="jane@test.com"),
#         ]
#         result = service.create_all(session, data)
#         assert len(result) == 2
#         assert result[0].name == "John"
#         assert result[1].name == "Jane"


# class TestGetById:
#     def test_get_by_id_returns_response(
#         self,
#         service: SqlAlchemyCrudService[
#             User, CreateUserRequest, UpdateUserRequest, UserResponse, int
#         ],
#         session: Session,
#     ) -> None:
#         created = service.create(session, CreateUserRequest(name="John", email="john@test.com"))
#         result = service.get_by_id(session, created.id)
#         assert result is not None
#         assert result.name == "John"

#     def test_get_by_id_returns_none_for_nonexistent(
#         self,
#         service: SqlAlchemyCrudService[
#             User, CreateUserRequest, UpdateUserRequest, UserResponse, int
#         ],
#         session: Session,
#     ) -> None:
#         result = service.get_by_id(session, 999)
#         assert result is None


# class TestExistsById:
#     def test_exists_by_id_true(
#         self,
#         service: SqlAlchemyCrudService[
#             User, CreateUserRequest, UpdateUserRequest, UserResponse, int
#         ],
#         session: Session,
#     ) -> None:
#         created = service.create(session, CreateUserRequest(name="John", email="john@test.com"))
#         assert service.exists_by_id(session, created.id) is True

#     def test_exists_by_id_false(
#         self,
#         service: SqlAlchemyCrudService[
#             User, CreateUserRequest, UpdateUserRequest, UserResponse, int
#         ],
#         session: Session,
#     ) -> None:
#         assert service.exists_by_id(session, 999) is False


# class TestGetAll:
#     def test_get_all_returns_responses(
#         self,
#         service: SqlAlchemyCrudService[
#             User, CreateUserRequest, UpdateUserRequest, UserResponse, int
#         ],
#         session: Session,
#     ) -> None:
#         service.create(session, CreateUserRequest(name="John", email="john@test.com"))
#         service.create(session, CreateUserRequest(name="Jane", email="jane@test.com"))
#         result = service.get_all(session)
#         assert len(result) == 2

#     def test_get_all_empty(
#         self,
#         service: SqlAlchemyCrudService[
#             User, CreateUserRequest, UpdateUserRequest, UserResponse, int
#         ],
#         session: Session,
#     ) -> None:
#         result = service.get_all(session)
#         assert result == []


# class TestGetAllById:
#     def test_get_all_by_id_returns_responses(
#         self,
#         service: SqlAlchemyCrudService[
#             User, CreateUserRequest, UpdateUserRequest, UserResponse, int
#         ],
#         session: Session,
#     ) -> None:
#         u1 = service.create(session, CreateUserRequest(name="John", email="john@test.com"))
#         u2 = service.create(session, CreateUserRequest(name="Jane", email="jane@test.com"))
#         result = service.get_all_by_id(session, [u1.id, u2.id])
#         assert len(result) == 2

#     def test_get_all_by_id_filters_nonexistent(
#         self,
#         service: SqlAlchemyCrudService[
#             User, CreateUserRequest, UpdateUserRequest, UserResponse, int
#         ],
#         session: Session,
#     ) -> None:
#         u1 = service.create(session, CreateUserRequest(name="John", email="john@test.com"))
#         result = service.get_all_by_id(session, [u1.id, 999])
#         assert len(result) == 1


# class TestCount:
#     def test_count_returns_int(
#         self,
#         service: SqlAlchemyCrudService[
#             User, CreateUserRequest, UpdateUserRequest, UserResponse, int
#         ],
#         session: Session,
#     ) -> None:
#         service.create(session, CreateUserRequest(name="John", email="john@test.com"))
#         service.create(session, CreateUserRequest(name="Jane", email="jane@test.com"))
#         assert service.count(session) == 2

#     def test_count_empty(
#         self,
#         service: SqlAlchemyCrudService[
#             User, CreateUserRequest, UpdateUserRequest, UserResponse, int
#         ],
#         session: Session,
#     ) -> None:
#         assert service.count(session) == 0


# class TestUpdate:
#     def test_update_returns_response(
#         self,
#         service: SqlAlchemyCrudService[
#             User, CreateUserRequest, UpdateUserRequest, UserResponse, int
#         ],
#         session: Session,
#     ) -> None:
#         created = service.create(session, CreateUserRequest(name="John", email="john@test.com"))
#         result = service.update(
#             session,
#             created.id,
#             UpdateUserRequest(name="John Doe", email="johndoe@test.com"),
#         )
#         assert result is not None
#         assert result.name == "John Doe"
#         assert result.email == "johndoe@test.com"

#     def test_update_returns_none_for_nonexistent(
#         self,
#         service: SqlAlchemyCrudService[
#             User, CreateUserRequest, UpdateUserRequest, UserResponse, int
#         ],
#         session: Session,
#     ) -> None:
#         result = service.update(session, 999, UpdateUserRequest(name="John", email="john@test.com"))
#         assert result is None


# class TestDelete:
#     def test_delete_removes_entity(
#         self,
#         service: SqlAlchemyCrudService[
#             User, CreateUserRequest, UpdateUserRequest, UserResponse, int
#         ],
#         session: Session,
#     ) -> None:
#         created = service.create(session, CreateUserRequest(name="John", email="john@test.com"))
#         service.delete(session, created.id)
#         assert service.count(session) == 0

#     def test_delete_handles_nonexistent(
#         self,
#         service: SqlAlchemyCrudService[
#             User, CreateUserRequest, UpdateUserRequest, UserResponse, int
#         ],
#         session: Session,
#     ) -> None:
#         service.delete(session, 999)
#         assert service.count(session) == 0


# class TestDeleteById:
#     def test_delete_by_id_removes_entity(
#         self,
#         service: SqlAlchemyCrudService[
#             User, CreateUserRequest, UpdateUserRequest, UserResponse, int
#         ],
#         session: Session,
#     ) -> None:
#         created = service.create(session, CreateUserRequest(name="John", email="john@test.com"))
#         service.delete_by_id(session, created.id)
#         assert service.count(session) == 0


# class TestDeleteAll:
#     def test_delete_all_removes_all(
#         self,
#         service: SqlAlchemyCrudService[
#             User, CreateUserRequest, UpdateUserRequest, UserResponse, int
#         ],
#         session: Session,
#     ) -> None:
#         service.create(session, CreateUserRequest(name="John", email="john@test.com"))
#         service.create(session, CreateUserRequest(name="Jane", email="jane@test.com"))
#         service.delete_all(session)
#         assert service.count(session) == 0


# class TestDeleteAllById:
#     def test_delete_all_by_id_removes_specified(
#         self,
#         service: SqlAlchemyCrudService[
#             User, CreateUserRequest, UpdateUserRequest, UserResponse, int
#         ],
#         session: Session,
#     ) -> None:
#         u1 = service.create(session, CreateUserRequest(name="John", email="john@test.com"))
#         u2 = service.create(session, CreateUserRequest(name="Jane", email="jane@test.com"))
#         service.delete_all_by_id(session, [u1.id])
#         assert service.count(session) == 1
#         assert service.exists_by_id(session, u2.id) is True


# class TestFindAllWithFilter:
#     def test_find_all_with_limit(
#         self,
#         service: SqlAlchemyCrudService[
#             User, CreateUserRequest, UpdateUserRequest, UserResponse, int
#         ],
#         session: Session,
#     ) -> None:
#         service.create(session, CreateUserRequest(name="John", email="john@test.com"))
#         service.create(session, CreateUserRequest(name="Jane", email="jane@test.com"))
#         service.create(session, CreateUserRequest(name="Bob", email="bob@test.com"))
#         filters = SaFilter(limit=2)
#         result = service.get_all(session, filters=filters)
#         assert len(result) == 2

#     def test_find_all_with_offset(
#         self,
#         service: SqlAlchemyCrudService[
#             User, CreateUserRequest, UpdateUserRequest, UserResponse, int
#         ],
#         session: Session,
#     ) -> None:
#         service.create(session, CreateUserRequest(name="John", email="john@test.com"))
#         service.create(session, CreateUserRequest(name="Jane", email="jane@test.com"))
#         service.create(session, CreateUserRequest(name="Bob", email="bob@test.com"))
#         filters = SaFilter(offset=1)
#         result = service.get_all(session, filters=filters)
#         assert len(result) == 2


# class TestCountWithFilter:
#     def test_count_with_filter(
#         self,
#         service: SqlAlchemyCrudService[
#             User, CreateUserRequest, UpdateUserRequest, UserResponse, int
#         ],
#         session: Session,
#     ) -> None:
#         service.create(session, CreateUserRequest(name="John", email="john@test.com"))
#         service.create(session, CreateUserRequest(name="Jane", email="jane@test.com"))
#         service.create(session, CreateUserRequest(name="Bob", email="bob@test.com"))
#         filters = SaFilter(conditions=[User.name == "John"])
#         result = service.count(session, filters=filters)
#         assert result == 1
