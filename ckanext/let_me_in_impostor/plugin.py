from __future__ import annotations

import time

import ckan.plugins as p
import ckan.plugins.toolkit as tk
from ckan.common import session

from ckanext.let_me_in_impostor.model import ImpostorSession


@tk.blanket.blueprints
@tk.blanket.helpers
class LetMeInImpostorPlugin(p.SingletonPlugin):
    p.implements(p.IConfigurer)
    p.implements(p.IAuthenticator, inherit=True)

    # IConfigurer

    def update_config(self, config_: p.toolkit.CKANConfig):
        p.toolkit.add_template_directory(config_, "templates")
        p.toolkit.add_resource("assets", "let_me_in_impostor")

    # IAuthenticator

    def identify(self) -> None:
        if tk.get_endpoint() in {("static", "index"), ("webassets", "index")}:
            return

        session_id = session.get("lmi_impostor_session_id")

        imp_session = ImpostorSession.get(session_id)

        if not imp_session:
            return

        if imp_session.expires < time.time() or not imp_session.active:
            tk.logout_user()
            tk.login_user(imp_session.user)

            session.pop("lmi_impostor_session_id", None)

            imp_session.expire()

            tk.h.flash_success(tk._("You have been logged out of burrowed identity."))
