from __future__ import annotations

from typing import Any

from ckan import model
from ckan.plugins.interfaces import Interface


class ILetMeIn(Interface):
    """Interface to do something on user login via OTL link."""

    def manage_user(self, user: model.User, context: dict[str, Any]) -> model.User:
        """Manage a user object before login.

        Accept a user object that will be logged. Only Active user could be
        logged in, so here we could implement user re-activation, for example.

        The user is always exists, otherwise we are not getting here.

        This happend before we are checking for user state and actual login

        You can use context to pass some information further, for example, if you
        did something to user in `manage_user`, you can pass this information
        to `before_otl_login` or `after_otl_login` funcs.

        Must return a user object
        """
        return user

    def before_otl_login(self, user: model.User, context: dict[str, Any]) -> None:
        """Hook before user login.

        Allows to do something before we are logging in a user.
        Happens after all checks and `manage_user` method.
        """

    def after_otl_login(self, user: model.User, context: dict[str, Any]) -> None:
        """Hook after user login."""
