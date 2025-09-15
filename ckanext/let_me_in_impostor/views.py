from __future__ import annotations

import time
from typing import cast

from flask import Blueprint, Response
from flask.views import MethodView

import ckan.plugins.toolkit as tk
from ckan import model
from ckan.common import session

import ckanext.let_me_in.config as lmi_config
import ckanext.let_me_in.utils as lmi_utils
from ckanext.let_me_in_impostor.model import ImpostorSession

bp = Blueprint("let_me_in_impostor", __name__, url_prefix="/ckan-admin")


def before_request() -> None:
    """A before request handler to check for sysadmin rights."""
    if tk.request.endpoint == "let_me_in_impostor.return_identity":
        return

    try:
        tk.check_access("sysadmin", {"user": tk.current_user.name})
    except tk.NotAuthorized:
        tk.abort(403, tk._("Need to be system administrator to administer"))


class ImpostorView(MethodView):
    def get(self) -> str:
        return tk.render("let_me_in_impostor/impostor.html")


class BurrowIdentityView(MethodView):
    def post(self) -> Response:
        if session.get("lmi_impostor_user_id"):
            tk.h.flash_error(
                tk._("You are already impersonating another user"), "error"
            )
            return tk.redirect_to(tk.url_for("home"))

        user = self._get_user(tk.request.form.get("user_id", ""))
        ttl = lmi_config.get_impostor_ttl()

        session["lmi_impostor_user_id"] = tk.current_user.id
        session["lmi_impostor_expires"] = time.time() + ttl

        ImpostorSession.create(
            user_id=tk.current_user.id,
            target_user_id=user.id,
            expires=session["lmi_impostor_expires"],
        )

        tk.login_user(user)

        tk.h.flash_success(
            tk._("You are now impersonating user: %s for %d seconds")
            % (user.name, ttl),
            "success",
        )

        return tk.redirect_to(tk.url_for("home"))

    def _get_user(self, user_id: str) -> model.User:
        user_id = tk.request.form.get("user_id")

        if not user_id:
            tk.h.flash_error(tk._("No user selected"), "error")
            tk.redirect_to(tk.url_for("let_me_in_impostor.impostor"))

        user = lmi_utils.get_user(user_id)

        if user is None:
            tk.h.flash_error(tk._("User not found"), "error")
            tk.redirect_to(tk.url_for("let_me_in_impostor.impostor"))

        user = cast(model.User, user)

        if user.state != model.State.ACTIVE:
            tk.h.flash_error(tk._("User is not active. Can't login"))
            tk.redirect_to("user.login")

        return user


class ReturnIdentityView(MethodView):
    def post(self) -> Response:
        original_user_id = session.pop("lmi_impostor_user_id", None)
        session.pop("lmi_impostor_expires", None)

        active_session = ImpostorSession.get(original_user_id, tk.current_user.id)

        if not active_session:
            tk.h.flash_error(tk._("No active impersonation session found"), "error")
            return tk.redirect_to(tk.url_for("home"))

        original_user = cast(model.User, model.User.get(original_user_id))

        active_session.expire()

        tk.login_user(original_user)

        lmi_utils.update_user_last_active(original_user)

        tk.h.flash_success(
            tk._("You have returned to your original identity."), "success"
        )

        return tk.redirect_to(tk.url_for("home"))


bp.before_request(before_request)

bp.add_url_rule("/impostor", view_func=ImpostorView.as_view("impostor"))
bp.add_url_rule(
    "/burrow-identity", view_func=BurrowIdentityView.as_view("burrow_identity")
)
bp.add_url_rule(
    "/return-identity", view_func=ReturnIdentityView.as_view("return_identity")
)
