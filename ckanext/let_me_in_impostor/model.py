from __future__ import annotations

import logging
from datetime import datetime as dt
from datetime import timezone as tz

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Table
from sqlalchemy.orm import Mapped, relationship
from typing_extensions import Self

import ckan.plugins.toolkit as tk
from ckan import model
from ckan.model.types import make_uuid

log = logging.getLogger(__name__)


class ImpostorSession(tk.BaseModel):
    """Model for storing Impostor session information."""

    class State:
        active = "active"
        expired = "expired"
        terminated = "terminated"

    __table__ = Table(
        "lmi_impostor_session",
        tk.BaseModel.metadata,
        Column("id", String, primary_key=True, default=make_uuid),
        Column(
            "user_id",
            String,
            ForeignKey("user.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        Column(
            "target_user_id",
            String,
            ForeignKey("user.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        Column("created", DateTime(timezone=True), default=lambda: dt.now(tz=tz.utc)),
        Column("expires", Integer, nullable=False),
        Column("state", String, nullable=False, default="active"),
    )

    id: Mapped[str]
    user_id: Mapped[str]
    target_user_id: Mapped[str]
    created: Mapped[dt]
    expires: Mapped[int]
    state: Mapped[str]

    user: Mapped[model.User] = relationship("User", foreign_keys=[__table__.c.user_id])  # type: ignore
    target_user: Mapped[model.User] = relationship("User", foreign_keys=[__table__.c.target_user_id])  # type: ignore

    @classmethod
    def get(cls, session_id: str) -> Self | None:
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
            return model.Session.query(cls).filter(cls.state == state).order_by(cls.created.desc()).all()

        return model.Session.query(cls).order_by(cls.created.desc()).all()

    @property
    def active(self) -> bool:
        return bool(self.state == self.State.active)

    @classmethod
    def clear_history(cls) -> None:
        """Remove all history records."""
        model.Session.query(cls).delete()
        model.Session.commit()
