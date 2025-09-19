from __future__ import annotations

from collections.abc import Callable
from datetime import datetime

import pytest
from sqlalchemy.exc import IntegrityError

import ckan.tests.factories as factories
from ckan import model

from ckanext.let_me_in_impostor.model import ImpostorSession


@pytest.mark.usefixtures("with_plugins", "reset_db_once")
class TestImpostorSessionModel:
    def test_get_session_missing(self):
        assert not ImpostorSession.get("nonexistent-id")

    def test_create_session(self, impostor_session: ImpostorSession):
        assert impostor_session.user_id
        assert impostor_session.target_user_id
        assert impostor_session.state == ImpostorSession.State.active
        assert impostor_session.id
        assert isinstance(impostor_session.created, datetime)

        # relationships
        assert isinstance(impostor_session.user, model.User)
        assert isinstance(impostor_session.target_user, model.User)

    def test_get_session(self, impostor_session: ImpostorSession):
        """The session can be retrieved by session ID."""
        assert ImpostorSession.get(impostor_session.id)

    def test_create_for_missing_user(self, impostor_session_factory: Callable[..., ImpostorSession]):
        user = factories.User()

        with pytest.raises(IntegrityError):
            impostor_session_factory(user_id="missing-user-id", target_user_id=user["id"], expires=3600)

        model.Session.rollback()

        with pytest.raises(IntegrityError):
            impostor_session_factory(user_id=user["id"], target_user_id="missing-user-id", expires=3600)

    def test_expire_session(self, impostor_session: ImpostorSession):
        assert impostor_session.state == ImpostorSession.State.active
        assert impostor_session.active

        impostor_session.expire()

        assert impostor_session.state == ImpostorSession.State.expired

    def test_terminate_session(self, impostor_session: ImpostorSession):
        assert impostor_session.active

        impostor_session.terminate()

        assert impostor_session.state == ImpostorSession.State.terminated

    def test_active_property(self, impostor_session: ImpostorSession):
        assert impostor_session.active

        impostor_session.expire()
        assert not impostor_session.active

    def test_all_sessions_no_filter(self, impostor_session_factory: Callable[..., ImpostorSession]):
        session1 = impostor_session_factory()
        session2 = impostor_session_factory()
        session2.expire()
        session3 = impostor_session_factory()
        session3.terminate()

        all_sessions = ImpostorSession.all()
        session_ids = [s.id for s in all_sessions]

        assert session1.id in session_ids
        assert session2.id in session_ids
        assert session3.id in session_ids

    def test_all_sessions_with_state_filter(self, impostor_session_factory: Callable[..., ImpostorSession]):
        active_session = impostor_session_factory()
        expired_session = impostor_session_factory()
        expired_session.expire()
        terminated_session = impostor_session_factory()
        terminated_session.terminate()

        # Test active filter
        active_sessions = ImpostorSession.all(state=ImpostorSession.State.active)
        active_ids = [s.id for s in active_sessions]
        assert active_session.id in active_ids
        assert expired_session.id not in active_ids
        assert terminated_session.id not in active_ids

        # Test expired filter
        expired_sessions = ImpostorSession.all(state=ImpostorSession.State.expired)
        expired_ids = [s.id for s in expired_sessions]
        assert active_session.id not in expired_ids
        assert expired_session.id in expired_ids
        assert terminated_session.id not in expired_ids

    def test_sessions_ordered_by_created_desc(self, impostor_session_factory: Callable[..., ImpostorSession]):
        session1 = impostor_session_factory()
        session2 = impostor_session_factory()
        session3 = impostor_session_factory()

        # Find our sessions in the results
        test_sessions = [s for s in ImpostorSession.all() if s.id in [session1.id, session2.id, session3.id]]

        # Should be ordered by creation date descending (newest first)
        assert len(test_sessions) == 3
        assert test_sessions[0].created >= test_sessions[1].created
        assert test_sessions[1].created >= test_sessions[2].created

    def test_clear_history(self, impostor_session_factory: Callable[..., ImpostorSession]):
        for _ in range(10):
            impostor_session_factory()

        # we should have at least 10 sessions now, as we clear the DB only once
        assert len(ImpostorSession.all()) >= 10

        ImpostorSession.clear_history()

        assert len(ImpostorSession.all()) == 0
