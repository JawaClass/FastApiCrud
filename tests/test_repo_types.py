# from __future__ import annotations

# from sqlalchemy.orm import Session

# from .conftest import User
# from src.repository import SqlAlchemyCrudRepository
# from src.repository.crud_filter import SaFilter


# def test_repo(session: Session):

#     repo: SqlAlchemyCrudRepository[User, int] = SqlAlchemyCrudRepository(
#         model_class=User, id_column=User.id
#     )

#     assert repo.count(session=session) == 0

#     found_user = repo.find_by_id(session=session, id=1)

#     assert found_user is None

#     created_user = repo.save(session=session, entity=User(name="User1", email="email@email.com"))

#     created_user_id = created_user.id

#     assert created_user is not None

#     found_user = repo.find_by_id(session=session, id=created_user_id)

#     assert found_user is not None
#     assert isinstance(found_user, User)
#     assert found_user.id == created_user_id

#     assert repo.count(session=session) == 1

#     repo.delete_by_id(session=session, id=created_user_id)

#     found_user = repo.find_by_id(session=session, id=created_user_id)

#     assert found_user is None

#     created_user = repo.save(session=session, entity=User(name="User1", email="email@email.com"))

#     created_user_id = created_user.id

#     assert created_user is not None

#     found_user = repo.find_by_id(session=session, id=created_user_id)

#     assert found_user is not None
#     assert isinstance(found_user, User)
#     assert found_user.id == created_user_id
#     assert repo.count(session=session) == 1

#     repo.delete_by_id(session=session, id=created_user_id)

#     found_user = repo.find_by_id(session=session, id=created_user_id)

#     assert found_user is None

#     created_user = repo.save(session=session, entity=User(name="User1", email="email@email.com"))

#     created_user_id = created_user.id

#     assert created_user is not None

#     found_user = repo.find_by_id(session=session, id=created_user_id)

#     assert found_user is not None
#     assert isinstance(found_user, User)
#     assert found_user.id == created_user_id

#     assert repo.count(session=session) == 1

#     assert (
#         repo.count(session=session, filters=SaFilter(conditions=[User.name == created_user.name]))
#         == 1
#     )

#     assert repo.count(session=session, filters=SaFilter(conditions=[User.name == ""])) == 0

#     repo.delete_by_id(session=session, id=created_user_id)

#     found_user = repo.find_by_id(session=session, id=created_user_id)

#     assert found_user is None
