from __future__ import annotations

from datetime import timedelta
from typing import cast

import pytest

import ckan.model as model
from ckan.tests.helpers import call_action

HOUR = 3600
SECOND = 1
EXPIRED = True


@pytest.mark.usefixtures("non_clean_db", "with_plugins")
class TestOTLViews:
    def test_login_user_with_otl(self, app, user):
        otl = call_action("lmi_generate_otl", uid=user["id"])

        assert "You have been logged in" in app.get(otl["url"]).body

        assert "You have tried to use a one-time login link that has expired" in app.get(otl["url"]).body

    def test_user_login_expires_the_otl(self, app, user):
        """Test OTL expiration on user login.

        We are not creating any entity for OTL. It expires right after the
        user it was created for is logged in. This triggers the update of
        `last_active` field and if the OTL is older than this, it will be invalidated
        """
        otl = call_action("lmi_generate_otl", uid=user["id"])

        user = cast(model.User, model.User.get(user["id"]))
        user.set_user_last_active()

        assert "You have tried to use a one-time login link that has expired" in app.get(otl["url"]).body

    def test_visit_link_after_user_has_been_deleted(self, app, user):
        otl = call_action("lmi_generate_otl", uid=user["id"])

        user = cast(model.User, model.User.get(user["id"]))
        user.purge()
        user.commit()

        assert "Invalid login link" in app.get(otl["url"]).body

    @pytest.mark.parametrize(
        ("delta_kwargs", "expired"),
        [
            ({"days": 1, "hours": 1}, True),
            ({"hours": 23}, False),
        ],
    )
    def test_otl_time_expiration(self, app, freezer, user, delta_kwargs, expired):
        """Test OTL link expiration.

        Each OTL link has an expiration date, that is configurable.
        """
        otl = call_action("lmi_generate_otl", uid=user["id"])

        freezer.move_to(timedelta(**delta_kwargs))

        resp_body: str = app.get(otl["url"]).body

        err_msg = "The login link has expired. Please request a new one"
        assert err_msg in resp_body if expired else err_msg not in resp_body

    def test_user_is_not_active(self, app, user_factory):
        """If user is not Active, we can't login."""
        user = user_factory(state=model.State.DELETED)
        otl = call_action("lmi_generate_otl", uid=user["id"])

        assert "User is not active" in app.get(otl["url"]).body

    @pytest.mark.parametrize(
        ("delta_kwargs", "ttl", "expired"),
        [
            ({"minutes": 5}, SECOND, EXPIRED),
            ({"hours": 2}, HOUR, EXPIRED),
            ({"hours": 2}, HOUR * 3, not EXPIRED),
        ],
    )
    def test_custom_otl_ttl(self, app, freezer, user, delta_kwargs, ttl, expired):
        """We can set custom TTL for each generated OTL link."""
        otl = call_action("lmi_generate_otl", uid=user["id"], ttl=ttl)

        freezer.move_to(timedelta(**delta_kwargs))

        resp_body: str = app.get(otl["url"]).body

        err_msg = "The login link has expired. Please request a new one"
        assert err_msg in resp_body if expired else err_msg not in resp_body
