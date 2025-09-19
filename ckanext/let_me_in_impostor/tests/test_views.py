from __future__ import annotations

from collections.abc import Callable
from datetime import datetime, timedelta
from typing import Any
from unittest.mock import patch

import pytest
from freezegun import freeze_time

import ckan.model as model
import ckan.tests.factories as factories

from ckanext.let_me_in_impostor.model import ImpostorSession


@pytest.mark.usefixtures("with_plugins", "reset_db_once")
class TestImpostorViews:
    def test_impostor_view_requires_sysadmin(self, app, user: dict[str, Any]):
        """Regular users can't access impostor view."""
        resp = app.get("/ckan-admin/impostor", headers={"REMOTE_USER": user["token"]})

        assert resp.status_code == 403

    def test_impostor_view_sysadmin_access(self, app, sysadmin: dict[str, Any]):
        """Sysadmin can access impostor view."""
        resp = app.get("/ckan-admin/impostor", headers={"Authorization": sysadmin["token"]})

        assert resp.status_code == 200
        assert "Impostor Sessions" in resp.body or "sessions" in resp.body

    def test_impostor_view_shows_sessions(self, app, sysadmin: dict[str, Any], impostor_session: ImpostorSession):
        """Impostor view displays existing sessions."""
        resp = app.get("/ckan-admin/impostor", headers={"Authorization": sysadmin["token"]})

        assert resp.status_code == 200

        assert impostor_session.user.display_name in resp.body
        assert impostor_session.target_user.display_name in resp.body
        assert impostor_session.state in resp.body

    def test_impostor_view_shows_otl_link(self, app, sysadmin: dict[str, Any]):
        """Impostor view displays OTL link when provided."""
        otl_url = "http://example.com/otl/link"

        resp = app.get(
            f"/ckan-admin/impostor?otl_link={otl_url}",
            headers={"Authorization": sysadmin["token"]},
        )

        assert resp.status_code == 200
        assert otl_url in resp.body

    def test_impostor_view_expires_old_sessions(
        self,
        app,
        sysadmin: dict[str, Any],
        user_factory: Callable[..., dict[str, Any]],
        impostor_session_factory: Callable[..., ImpostorSession],
    ):
        """Impostor view automatically expires old sessions."""
        user = user_factory()
        target_user = user_factory()

        # Create a session that expires in the past
        past_time = 3600  # 1 hour ago
        old_session = impostor_session_factory(user_id=user["id"], target_user_id=target_user["id"], expires=past_time)

        with freeze_time(datetime.now() + timedelta(days=1)):  # noqa: DTZ005
            app.get("/ckan-admin/impostor", headers={"Authorization": sysadmin["token"]})

        refreshed_session = ImpostorSession.get(old_session.id)
        assert refreshed_session is not None
        assert refreshed_session.state == ImpostorSession.State.expired


@pytest.mark.usefixtures("with_plugins", "reset_db_once")
class TestBurrowIdentityView:
    def test_burrow_identity_requires_sysadmin(self, app, user_factory: Callable[..., dict[str, Any]]):
        """Regular users can't burrow identity."""
        user = user_factory()
        target_user = user_factory()

        resp = app.post(
            "/ckan-admin/burrow-identity",
            data={"user_id": target_user["id"]},
            environ_overrides={"REMOTE_USER": user["name"]},
        )

        assert resp.status_code == 403

    def test_burrow_identity_success(self, app, user: dict[str, Any], sysadmin: dict[str, Any]):
        """Sysadmin can successfully burrow identity."""
        resp = app.post(
            "/ckan-admin/burrow-identity",
            data={"user_id": user["id"]},
            headers={"Authorization": sysadmin["token"]},
        )

        assert user["display_name"] in resp.body

    def test_burrow_identity_creates_session(self, app, user: dict[str, Any], sysadmin: dict[str, Any]):
        """Burrowing identity creates impostor session."""
        user = factories.User()

        app.post(
            "/ckan-admin/burrow-identity",
            data={"user_id": user["id"]},
            headers={"Authorization": sysadmin["token"]},
        )

        sessions = ImpostorSession.all(state=ImpostorSession.State.active)
        assert len(sessions) >= 1

        session = sessions[0]
        assert session.user_id == sysadmin["id"]
        assert session.target_user_id == user["id"]

    def test_burrow_identity_no_user_selected(self, app, sysadmin: dict[str, Any]):
        """Burrowing identity fails without user selection."""
        resp = app.post(
            "/ckan-admin/burrow-identity",
            data={},
            headers={"Authorization": sysadmin["token"]},
        )

        assert resp.status_code == 200
        assert "Active user not found" in resp.body

    def test_burrow_identity_invalid_user(self, app, sysadmin: dict[str, Any]):
        """Burrowing identity fails with invalid user."""
        resp = app.post(
            "/ckan-admin/burrow-identity",
            data={"user_id": "nonexistent-user-id"},
            headers={"Authorization": sysadmin["token"]},
        )

        assert resp.status_code == 200
        assert "Active user not found" in resp.body

    def test_burrow_identity_inactive_user(
        self, app, sysadmin: dict[str, Any], user_factory: Callable[..., dict[str, Any]]
    ):
        """Burrowing identity fails with inactive user."""
        inactive_user = user_factory(state=model.State.DELETED)

        resp = app.post(
            "/ckan-admin/burrow-identity",
            data={"user_id": inactive_user["id"]},
            headers={"Authorization": sysadmin["token"]},
        )

        assert resp.status_code == 200
        assert "Active user not found" in resp.body

    @patch("ckanext.let_me_in_impostor.views.tk.h.lmi_is_current_user_an_impostor")
    def test_burrow_identity_already_impersonating(self, mock_is_impostor, app, sysadmin: dict[str, Any]):
        """Can't burrow identity when already impersonating."""
        mock_is_impostor.return_value = True
        target_user = factories.User()

        resp = app.post(
            "/ckan-admin/burrow-identity",
            data={"user_id": target_user["id"]},
            headers={"Authorization": sysadmin["token"]},
        )

        assert resp.status_code == 200
        assert "You are already impersonating another user" in resp.body


@pytest.mark.usefixtures("with_plugins", "reset_db_once")
class TestReturnIdentityView:
    def test_return_identity_success(
        self,
        app,
        impostor_session_factory: Callable[..., ImpostorSession],
        user: dict[str, Any],
        sysadmin: dict[str, Any],
    ):
        """Successfully return to original identity."""
        client = app.flask_app.test_client()
        impostor_session = impostor_session_factory(user_id=sysadmin["id"], target_user_id=user["id"])

        with client.session_transaction() as sess:
            sess["lmi_impostor_session_id"] = impostor_session.id

        resp = client.post(
            "/ckan-admin/return-identity",
            environ_overrides={"REMOTE_USER": impostor_session.target_user.name},
            follow_redirects=True,
        )

        data = resp.get_data(as_text=True)

        assert "You have returned to your original identity" in data
        assert impostor_session.user.display_name in data

        # Check session was expired
        refreshed_session = ImpostorSession.get(impostor_session.id)
        assert refreshed_session is not None
        assert refreshed_session.state == ImpostorSession.State.expired

    def test_return_identity_no_active_session(self, app, sysadmin: dict[str, Any]):
        """Return identity fails without active session."""
        resp = app.post(
            "/ckan-admin/return-identity",
            headers={"Authorization": sysadmin["token"]},
            follow_redirects=True,
        )

        data = resp.get_data(as_text=True)
        assert "No active impersonation session found" in data

    def test_return_identity_invalid_session(self, app, sysadmin: dict[str, Any]):
        """Return identity fails with invalid session."""
        client = app.flask_app.test_client()

        with client.session_transaction() as sess:
            sess["lmi_impostor_session_id"] = "invalid-session-id"

        resp = client.post(
            "/ckan-admin/return-identity",
            headers={"Authorization": sysadmin["token"]},
            follow_redirects=True,
        )

        data = resp.get_data(as_text=True)
        assert "No active impersonation session found" in data


@pytest.mark.usefixtures("with_plugins", "reset_db_once")
class TestTerminateSessionView:
    def test_terminate_session_requires_sysadmin(self, app, impostor_session):
        """Regular users can't terminate sessions."""
        user = factories.User()

        resp = app.post(
            "/ckan-admin/terminate-session",
            data={"session_id": impostor_session.id},
            environ_overrides={"REMOTE_USER": user["name"]},
        )

        assert resp.status_code == 403

    def test_terminate_session_success(self, app, sysadmin: dict[str, Any], impostor_session: ImpostorSession):
        """Sysadmin can terminate sessions."""
        resp = app.post(
            "/ckan-admin/terminate-session",
            data={"session_id": impostor_session.id},
            headers={"Authorization": sysadmin["token"]},
            follow_redirects=True,
        )

        data = resp.get_data(as_text=True)

        assert "The impersonation session has been terminated" in data

        # Check session was terminated
        session = ImpostorSession.get(impostor_session.id)
        assert session is not None
        assert session.state == ImpostorSession.State.terminated

    def test_terminate_session_not_found(self, app, sysadmin: dict[str, Any]):
        """Terminating non-existent session fails gracefully."""
        resp = app.post(
            "/ckan-admin/terminate-session",
            data={"session_id": "nonexistent-id"},
            headers={"Authorization": sysadmin["token"]},
            follow_redirects=True,
        )

        data = resp.get_data(as_text=True)
        assert "The impersonation session was not found" in data

    def test_terminate_session_no_session_id(self, app, sysadmin: dict[str, Any]):
        """Terminating without session ID fails gracefully."""
        resp = app.post(
            "/ckan-admin/terminate-session",
            headers={"Authorization": sysadmin["token"]},
            follow_redirects=True,
        )

        data = resp.get_data(as_text=True)
        assert "The impersonation session was not found" in data


@pytest.mark.usefixtures("with_plugins", "reset_db_once")
class TestClearSessionHistoryView:
    def test_clear_session_history_requires_sysadmin(self, app):
        """Regular users can't clear session history."""
        user = factories.User()

        resp = app.post(
            "/ckan-admin/clear-session-history",
            environ_overrides={"REMOTE_USER": user["name"]},
        )

        assert resp.status_code == 403

    def test_clear_session_history_success(
        self,
        app,
        sysadmin: dict[str, Any],
        impostor_session_factory: Callable[..., ImpostorSession],
    ):
        """Sysadmin can clear session history."""
        impostor_session_factory()
        assert len(ImpostorSession.all()) >= 1

        resp = app.post(
            "/ckan-admin/clear-session-history",
            headers={"Authorization": sysadmin["token"]},
        )

        data = resp.get_data(as_text=True)

        assert "Impersonation session history cleared" in data
        assert len(ImpostorSession.all()) == 0


@pytest.mark.usefixtures("with_plugins", "reset_db_once")
class TestGenerateOTLView:
    def test_generate_otl_requires_sysadmin(self, app, user_factory: Callable[..., dict[str, Any]]):
        """Regular users can't generate OTL."""
        user = user_factory()
        target_user = user_factory()

        resp = app.post(
            "/ckan-admin/generate-otl",
            data={"otl_user_id": target_user["id"]},
            environ_overrides={"REMOTE_USER": user["name"]},
        )

        assert resp.status_code == 403

    def test_generate_otl_success(self, app, sysadmin: dict[str, Any], user_factory: Callable[..., dict[str, Any]]):
        """Sysadmin can generate OTL."""
        target_user = user_factory()

        resp = app.post(
            "/ckan-admin/generate-otl",
            data={"otl_user_id": target_user["id"]},
            headers={"Authorization": sysadmin["token"]},
        )

        data = resp.get_data(as_text=True)
        assert "Your one-time login link has been generated" in data

    def test_generate_otl_no_user_selected(self, app, sysadmin: dict[str, Any]):
        """Generate OTL fails without user selection."""
        resp = app.post("/ckan-admin/generate-otl", headers={"Authorization": sysadmin["token"]})

        data = resp.get_data(as_text=True)
        assert "No active user found for" in data

    def test_generate_otl_inactive_user(
        self, app, sysadmin: dict[str, Any], user_factory: Callable[..., dict[str, Any]]
    ):
        """Generate OTL fails for inactive user."""
        inactive_user = user_factory(state=model.State.DELETED)

        resp = app.post(
            "/ckan-admin/generate-otl",
            data={"otl_user_id": inactive_user["id"]},
            headers={"Authorization": sysadmin["token"]},
        )

        data = resp.get_data(as_text=True)
        assert "No active user found for" in data

    def test_generate_otl_with_custom_ttl(
        self,
        app,
        sysadmin: dict[str, Any],
        user_factory: Callable[..., dict[str, Any]],
    ):
        """Generate OTL with custom TTL."""
        target_user = user_factory()
        custom_ttl = 7200  # 2 hours

        resp = app.post(
            "/ckan-admin/generate-otl",
            data={"otl_user_id": target_user["id"], "ttl": custom_ttl},
            headers={"Authorization": sysadmin["token"]},
        )

        data = resp.get_data(as_text=True)
        assert "Your one-time login link has been generated" in data
        assert f"It can be used only once and will expire either after use or in {custom_ttl} seconds" in data
