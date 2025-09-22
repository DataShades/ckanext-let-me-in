from __future__ import annotations

import time

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
        sessions = ImpostorSession.all()
        otl_link = tk.request.args.get("otl_link")
        otl_ttl = tk.request.args.get("otl_ttl")
        otl_user = tk.request.args.get("otl_user")

        self._check_expired_session()

        return tk.render(
            "let_me_in_impostor/impostor.html",
            extra_vars={
                "sessions": sessions,
                "otl_link": otl_link,
                "otl_ttl": otl_ttl,
                "otl_user": otl_user,
            },
        )

    def _check_expired_session(self) -> None:
        current_time = time.time()

        for imp_session in ImpostorSession.all(ImpostorSession.State.active):
            if imp_session.expires > current_time:
                continue

            imp_session.expire()


class BurrowIdentityView(MethodView):
    def post(self) -> Response:
        if tk.h.lmi_is_current_user_an_impostor():
            tk.h.flash_error(
                tk._("You are already impersonating another user"), "error"
            )
            return tk.redirect_to("let_me_in_impostor.impostor")

        ttl = lmi_config.get_impostor_ttl()
        user = lmi_utils.get_user(tk.request.form.get("user_id", ""))

        if not user or user.state != model.State.ACTIVE:
            tk.h.flash_error(tk._("Active user not found"), "error")
            return tk.redirect_to("let_me_in_impostor.impostor")

        imp_session = ImpostorSession.create(
            user_id=tk.current_user.id,
            target_user_id=user.id,
            expires=int(time.time() + ttl),
        )

        session["lmi_impostor_session_id"] = imp_session.id

        tk.login_user(user)

        tk.h.flash_success(
            tk._("You are now impersonating user %s for %d seconds") % (user.name, ttl),
            "success",
        )

        return tk.redirect_to("user.me")


class ReturnIdentityView(MethodView):
    def post(self) -> Response:
        session_id = session.pop("lmi_impostor_session_id", None)

        imp_session = ImpostorSession.get(session_id)

        if not imp_session:
            tk.h.flash_error(tk._("No active impersonation session found"), "error")
            return tk.redirect_to("user.me")

        imp_session.expire()

        tk.login_user(imp_session.user)
        lmi_utils.update_user_last_active(imp_session.user)

        tk.h.flash_success(
            tk._("You have returned to your original identity."), "success"
        )

        return tk.redirect_to("let_me_in_impostor.impostor")


class TerminateSessionView(MethodView):
    def post(self) -> Response:
        session_id = tk.request.form.get("session_id", "")
        session = ImpostorSession.get(session_id)

        if not session:
            tk.h.flash_error(tk._("The impersonation session was not found"), "error")
            return tk.redirect_to(tk.url_for("let_me_in_impostor.impostor"))

        session.terminate()

        tk.h.flash_success(
            tk._("The impersonation session has been terminated."), "success"
        )

        return tk.redirect_to(tk.url_for("let_me_in_impostor.impostor"))


class ClearSessionHistoryView(MethodView):
    def post(self) -> Response:
        ImpostorSession.clear_history()

        tk.h.flash_success(tk._("Impersonation session history cleared."), "success")

        return tk.redirect_to(tk.url_for("let_me_in_impostor.impostor"))


class GenerateOTLView(MethodView):
    def post(self) -> Response | str:
        user_id = tk.request.form.get("otl_user_id", "")
        ttl = tk.request.form.get("ttl", lmi_config.get_default_otl_link_ttl())

        user = lmi_utils.get_user(user_id)

        if user is None or user.state != model.State.ACTIVE:
            tk.h.flash_error(
                tk._("No active user found for {}. Can't generate OTL").format(user_id),
                "error",
            )
            return tk.redirect_to("let_me_in_impostor.impostor")

        try:
            result = tk.get_action("lmi_generate_otl")(
                {"ignore_auth": True},
                {"uid": user.id, "ttl": ttl},
            )
        except tk.ValidationError as e:
            tk.h.flash_error(
                tk._("Failed to generate OTL: {}").format(e.error_summary), "error"
            )
            return tk.redirect_to("let_me_in_impostor.impostor")

        return tk.redirect_to(
            "let_me_in_impostor.impostor",
            otl_link=result["url"],
            otl_ttl=ttl,
            otl_user=user.display_name,
        )


bp.before_request(before_request)

bp.add_url_rule("/impostor", view_func=ImpostorView.as_view("impostor"))
bp.add_url_rule(
    "/burrow-identity", view_func=BurrowIdentityView.as_view("burrow_identity")
)
bp.add_url_rule(
    "/return-identity", view_func=ReturnIdentityView.as_view("return_identity")
)
bp.add_url_rule(
    "/terminate-session", view_func=TerminateSessionView.as_view("terminate_session")
)
bp.add_url_rule(
    "/clear-session-history",
    view_func=ClearSessionHistoryView.as_view("clear_session_history"),
)
bp.add_url_rule("/generate-otl", view_func=GenerateOTLView.as_view("generate_otl"))
