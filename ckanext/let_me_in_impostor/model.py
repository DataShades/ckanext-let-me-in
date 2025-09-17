from __future__ import annotations

import logging
from datetime import datetime as dt
from datetime import timezone as tz
from typing import Any

from sqlalchemy import Column, DateTime, ForeignKey, Integer, Text, or_
from sqlalchemy.orm import relationship, Mapped
from typing_extensions import Self

import ckan.plugins.toolkit as tk
from ckan import model
from ckan.model.types import make_uuid

log = logging.getLogger(__name__)


class ImpostorSession(tk.BaseModel):
    """Model for storing Impostor session information."""

    __tablename__ = "lmi_impostor_session"

    class State:
        active = "active"
        expired = "expired"
        terminated = "terminated"

    id = Column(Text, primary_key=True, default=make_uuid)
    user_id = Column(
        Text,
        ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    target_user_id = Column(
        Text,
        ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    created = Column(DateTime(timezone=True), default=lambda: dt.now(tz=tz.utc))
    expires = Column(Integer, nullable=False)
    state = Column(Text, nullable=False, default=State.active)

    user: Mapped[model.User] = relationship("User", foreign_keys=[user_id])  # type: ignore
    target_user: Mapped[model.User] = relationship("User", foreign_keys=[target_user_id])  # type: ignore

    def dictize(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "target_user_id": self.target_user_id,
            "created": self.created,
            "expires": self.expires,
        }

    @classmethod
    def get(cls, session_id: str) -> Self | None:
        return model.Session.query(cls).filter_by(id=session_id).first()

    # @classmethod
    # def get(cls, original_user: str, target_user: str) -> Self | None:
    #     return (
    #         model.Session.query(cls)
    #         .filter_by(user_id=original_user)
    #         .filter_by(target_user_id=target_user)
    #         .first()
    #     )

    @classmethod
    def get_by_session_id(cls, session_id: str) -> Self | None:
        return model.Session.query(cls).filter_by(id=session_id).first()

    @classmethod
    def create(cls, user_id: str, target_user_id: str, expires: int) -> Self:
        session = cls(user_id=user_id, target_user_id=target_user_id, expires=expires)
        model.Session.add(session)
        model.Session.commit()
        return session

    def expire(self, defer_commit: bool = False) -> None:
        self.state = self.State.expired
        model.Session.add(self)

        if not defer_commit:
            model.Session.commit()

    def terminate(self) -> None:
        self.state = self.State.terminated
        model.Session.add(self)
        model.Session.commit()

    @classmethod
    def all(cls, state: str | None = None) -> list[Self]:
        if state:
            return (
                model.Session.query(cls)
                .filter(cls.state == state)
                .order_by(cls.created.desc())
                .all()
            )

        return model.Session.query(cls).order_by(cls.created.desc()).all()

    @property
    def active(self) -> bool:
        return bool(self.state == self.State.active)

    @classmethod
    def clear_history(cls) -> None:
        """Remove all history records."""
        model.Session.query(cls).delete()
        model.Session.commit()
