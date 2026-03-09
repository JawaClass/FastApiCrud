# from __future__ import annotations
# from sqlalchemy.orm import Session

# from src.repository import SaFilter, SqlAlchemyCrudRepository
# from .conftest import User


# class TestSave:
#     def test_save_returns_entity_with_id(
#         self, repository: SqlAlchemyCrudRepository[User, int], session: Session
#     ) -> None:
#         user = User(name="John", email="john@test.com")
#         result = repository.save(session, user)
#         assert result.id == 1
#         assert result.name == "John"

#     def test_save_persists_entity(
#         self, repository: SqlAlchemyCrudRepository[User, int], session: Session
#     ) -> None:
#         user = User(name="John", email="john@test.com")
#         repository.save(session, user)
#         users = session.query(User).all()
#         assert len(users) == 1


# class TestSaveAll:
#     def test_save_all_returns_entities_with_ids(
#         self, repository: SqlAlchemyCrudRepository[User, int], session: Session
#     ) -> None:
#         users = [
#             User(name="John", email="john@test.com"),
#             User(name="Jane", email="jane@test.com"),
#         ]
#         result = list(repository.save_all(session, users))
#         assert len(result) == 2
#         assert result[0].id == 1
#         assert result[1].id == 2


# class TestFindById:
#     def test_find_by_id_returns_entity(
#         self, repository: SqlAlchemyCrudRepository[User, int], session: Session
#     ) -> None:
#         user = User(name="John", email="john@test.com")
#         repository.save(session, user)
#         result = repository.find_by_id(session, 1)
#         assert result is not None
#         assert result.name == "John"

#     def test_find_by_id_returns_none_for_nonexistent(
#         self, repository: SqlAlchemyCrudRepository[User, int], session: Session
#     ) -> None:
#         result = repository.find_by_id(session, 999)
#         assert result is None


# class TestExistsById:
#     def test_exists_by_id_true(
#         self, repository: SqlAlchemyCrudRepository[User, int], session: Session
#     ) -> None:
#         user = User(name="John", email="john@test.com")
#         repository.save(session, user)
#         assert repository.exists_by_id(session, 1) is True

#     def test_exists_by_id_false(
#         self, repository: SqlAlchemyCrudRepository[User, int], session: Session
#     ) -> None:
#         assert repository.exists_by_id(session, 999) is False


# class TestFindAll:
#     def test_find_all_returns_all_entities(
#         self, repository: SqlAlchemyCrudRepository[User, int], session: Session
#     ) -> None:
#         repository.save(session, User(name="John", email="john@test.com"))
#         repository.save(session, User(name="Jane", email="jane@test.com"))
#         result = list(repository.find_all(session))
#         assert len(result) == 2

#     def test_find_all_empty(
#         self, repository: SqlAlchemyCrudRepository[User, int], session: Session
#     ) -> None:
#         result = list(repository.find_all(session))
#         assert result == []

#     def test_find_all_with_limit(
#         self, repository: SqlAlchemyCrudRepository[User, int], session: Session
#     ) -> None:
#         repository.save(session, User(name="John", email="john@test.com"))
#         repository.save(session, User(name="Jane", email="jane@test.com"))
#         repository.save(session, User(name="Bob", email="bob@test.com"))
#         filters = SaFilter(limit=2)
#         result = list(repository.find_all(session, filters=filters))
#         assert len(result) == 2

#     def test_find_all_with_offset(
#         self, repository: SqlAlchemyCrudRepository[User, int], session: Session
#     ) -> None:
#         repository.save(session, User(name="John", email="john@test.com"))
#         repository.save(session, User(name="Jane", email="jane@test.com"))
#         repository.save(session, User(name="Bob", email="bob@test.com"))
#         filters = SaFilter(offset=1)
#         result = list(repository.find_all(session, filters=filters))
#         assert len(result) == 2

#     def test_find_all_with_conditions(
#         self, repository: SqlAlchemyCrudRepository[User, int], session: Session
#     ) -> None:
#         repository.save(session, User(name="John", email="john@test.com"))
#         repository.save(session, User(name="Jane", email="jane@test.com"))
#         filters = SaFilter(conditions=[User.name == "John"])
#         result = list(repository.find_all(session, filters=filters))
#         assert len(result) == 1
#         assert result[0].name == "John"


# class TestFindAllById:
#     def test_find_all_by_id_returns_entities(
#         self, repository: SqlAlchemyCrudRepository[User, int], session: Session
#     ) -> None:
#         u1 = repository.save(session, User(name="John", email="john@test.com"))
#         u2 = repository.save(session, User(name="Jane", email="jane@test.com"))
#         result = list(repository.find_all_by_id(session, [u1.id, u2.id]))
#         assert len(result) == 2

#     def test_find_all_by_id_filters_nonexistent(
#         self, repository: SqlAlchemyCrudRepository[User, int], session: Session
#     ) -> None:
#         u1 = repository.save(session, User(name="John", email="john@test.com"))
#         result = list(repository.find_all_by_id(session, [u1.id, 999]))
#         assert len(result) == 1


# class TestCount:
#     def test_count_returns_int(
#         self, repository: SqlAlchemyCrudRepository[User, int], session: Session
#     ) -> None:
#         repository.save(session, User(name="John", email="john@test.com"))
#         repository.save(session, User(name="Jane", email="jane@test.com"))
#         assert repository.count(session) == 2

#     def test_count_empty(
#         self, repository: SqlAlchemyCrudRepository[User, int], session: Session
#     ) -> None:
#         assert repository.count(session) == 0

#     def test_count_with_filter(
#         self, repository: SqlAlchemyCrudRepository[User, int], session: Session
#     ) -> None:
#         repository.save(session, User(name="John", email="john@test.com"))
#         repository.save(session, User(name="Jane", email="jane@test.com"))
#         repository.save(session, User(name="Bob", email="bob@test.com"))
#         filters = SaFilter(conditions=[User.name == "John"])
#         result = repository.count(session, filters=filters)
#         assert result == 1


# class TestDelete:
#     def test_delete_removes_entity(
#         self, repository: SqlAlchemyCrudRepository[User, int], session: Session
#     ) -> None:
#         user = repository.save(session, User(name="John", email="john@test.com"))
#         repository.delete(session, user)
#         assert repository.count(session) == 0


# class TestDeleteById:
#     def test_delete_by_id_removes_entity(
#         self, repository: SqlAlchemyCrudRepository[User, int], session: Session
#     ) -> None:
#         user = repository.save(session, User(name="John", email="john@test.com"))
#         repository.delete_by_id(session, user.id)
#         assert repository.count(session) == 0

#     def test_delete_by_id_handles_nonexistent(
#         self, repository: SqlAlchemyCrudRepository[User, int], session: Session
#     ) -> None:
#         repository.delete_by_id(session, 999)
#         assert repository.count(session) == 0


# class TestDeleteAll:
#     def test_delete_all_removes_all(
#         self, repository: SqlAlchemyCrudRepository[User, int], session: Session
#     ) -> None:
#         repository.save(session, User(name="John", email="john@test.com"))
#         repository.save(session, User(name="Jane", email="jane@test.com"))
#         repository.delete_all(session)
#         assert repository.count(session) == 0


# class TestDeleteAllById:
#     def test_delete_all_by_id_removes_specified(
#         self, repository: SqlAlchemyCrudRepository[User, int], session: Session
#     ) -> None:
#         u1 = repository.save(session, User(name="John", email="john@test.com"))
#         u2 = repository.save(session, User(name="Jane", email="jane@test.com"))
#         repository.delete_all_by_id(session, [u1.id])
#         assert repository.count(session) == 1
#         assert repository.exists_by_id(session, u2.id) is True

#     def test_delete_all_by_id_handles_nonexistent(
#         self, repository: SqlAlchemyCrudRepository[User, int], session: Session
#     ) -> None:
#         u1 = repository.save(session, User(name="John", email="john@test.com"))
#         repository.delete_all_by_id(session, [u1.id, 999])
#         assert repository.count(session) == 0

#     def test_count_with_filter(
#         self, repository: SqlAlchemyCrudRepository, session: Session
#     ) -> None:
#         repository.save(session, User(name="John", email="john@test.com"))
#         repository.save(session, User(name="Jane", email="jane@test.com"))
#         repository.save(session, User(name="Bob", email="bob@test.com"))
#         filters = SaFilter(conditions=[User.name == "John"])
#         result = repository.count(session, filters=filters)
#         assert result == 1


# class TestDelete:
#     def test_delete_removes_entity(
#         self, repository: SqlAlchemyCrudRepository, session: Session
#     ) -> None:
#         user = repository.save(session, User(name="John", email="john@test.com"))
#         repository.delete(session, user)
#         assert repository.count(session) == 0


# class TestDeleteById:
#     def test_delete_by_id_removes_entity(
#         self, repository: SqlAlchemyCrudRepository, session: Session
#     ) -> None:
#         user = repository.save(session, User(name="John", email="john@test.com"))
#         repository.delete_by_id(session, user.id)
#         assert repository.count(session) == 0

#     def test_delete_by_id_handles_nonexistent(
#         self, repository: SqlAlchemyCrudRepository, session: Session
#     ) -> None:
#         repository.delete_by_id(session, 999)
#         assert repository.count(session) == 0


# class TestDeleteAll:
#     def test_delete_all_removes_all(
#         self, repository: SqlAlchemyCrudRepository, session: Session
#     ) -> None:
#         repository.save(session, User(name="John", email="john@test.com"))
#         repository.save(session, User(name="Jane", email="jane@test.com"))
#         repository.delete_all(session)
#         assert repository.count(session) == 0


# class TestDeleteAllById:
#     def test_delete_all_by_id_removes_specified(
#         self, repository: SqlAlchemyCrudRepository, session: Session
#     ) -> None:
#         u1 = repository.save(session, User(name="John", email="john@test.com"))
#         u2 = repository.save(session, User(name="Jane", email="jane@test.com"))
#         repository.delete_all_by_id(session, [u1.id])
#         assert repository.count(session) == 1
#         assert repository.exists_by_id(session, u2.id) is True

#     def test_delete_all_by_id_handles_nonexistent(
#         self, repository: SqlAlchemyCrudRepository, session: Session
#     ) -> None:
#         u1 = repository.save(session, User(name="John", email="john@test.com"))
#         repository.delete_all_by_id(session, [u1.id, 999])
#         assert repository.count(session) == 0
