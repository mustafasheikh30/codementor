from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from app.users.models import User
from app.users.schemas import CodeforcesIdentity


def _apply_identity(user: User, identity: CodeforcesIdentity) -> None:
    user.handle = identity.handle
    user.rating = identity.rating
    user.avatar = identity.avatar


def get_user_by_id(session: Session, user_id: int) -> User | None:
    return session.get(User, user_id)


def get_user_by_subject(session: Session, subject: str) -> User | None:
    statement = select(User).where(User.codeforces_subject == subject)
    return session.exec(statement).one_or_none()


def upsert_user(session: Session, identity: CodeforcesIdentity) -> User:
    user = get_user_by_subject(session, identity.subject)

    if user is None:
        user = User(codeforces_subject=identity.subject)
        _apply_identity(user, identity)
        session.add(user)
        try:
            session.commit()
        except IntegrityError:
            session.rollback()
            user = get_user_by_subject(session, identity.subject)
            if user is None:
                raise
            _apply_identity(user, identity)
            session.add(user)
            session.commit()
    else:
        _apply_identity(user, identity)
        session.add(user)
        session.commit()

    session.refresh(user)
    return user
