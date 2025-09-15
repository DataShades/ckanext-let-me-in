from __future__ import annotations

import logging
from datetime import datetime as dt
from datetime import timezone as tz
from typing import Any

from sqlalchemy import Column, DateTime, ForeignKey, Integer, Text
from sqlalchemy.orm import relationship
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

    user = relationship(
        "User", foreign_keys=[user_id], backref="lmi_impostor_sessions"
    )

    target_user = relationship("User", foreign_keys=[target_user_id])

    def dictize(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "target_user_id": self.target_user_id,
            "created": self.created,
            "expires": self.expires,
        }

    @classmethod
    def get(cls, original_user: str, target_user: str) -> Self | None:
        return (
            model.Session.query(cls)
            .filter_by(user_id=original_user)
            .filter_by(target_user_id=target_user)
            .filter_by(state=cls.State.active)
            .first()
        )

    @classmethod
    def create(cls, user_id: str, target_user_id: str, expires: int) -> Self:
        session = cls(user_id=user_id, target_user_id=target_user_id, expires=expires)
        model.Session.add(session)
        model.Session.commit()
        return session

    def expire(self) -> None:
        self.state = self.State.expired
        model.Session.add(self)
        model.Session.commit()

    @classmethod
    def list(cls, user_id: str) -> list[Self]:
        return model.Session.query(cls).filter_by(user_id=user_id).order_by(cls.created.desc()).all()

    @property
    def active(self) -> bool:
        return bool(self.state == self.State.active)
