from sqlmodel import select

from app.users import service
from app.users.models import User
from app.users.schemas import CodeforcesIdentity


def identity(
    handle: str = "alice",
    rating: int | None = 1500,
    avatar: str | None = "https://codeforces.org/avatar.png",
) -> CodeforcesIdentity:
    return CodeforcesIdentity(
        sub="cf-subject-123",
        handle=handle,
        rating=rating,
        avatar=avatar,
    )


def test_upsert_user_creates_one_account(session):
    user = service.upsert_user(session, identity())

    assert user.id is not None
    assert user.handle == "alice"
    assert service.get_user_by_subject(session, "cf-subject-123").id == user.id
    assert service.get_user_by_id(session, user.id).handle == "alice"
    assert len(session.exec(select(User)).all()) == 1


def test_upsert_user_updates_the_existing_account(session):
    first = service.upsert_user(session, identity())
    second = service.upsert_user(
        session,
        identity(handle="alice_v2", rating=1600, avatar=None),
    )

    assert second.id == first.id
    assert second.handle == "alice_v2"
    assert second.rating == 1600
    assert second.avatar is None
    assert len(session.exec(select(User)).all()) == 1


def test_unknown_users_return_none(session):
    assert service.get_user_by_id(session, 999) is None
    assert service.get_user_by_subject(session, "missing") is None
