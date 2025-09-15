from __future__ import annotations

import time

import ckan.plugins as p
import ckan.plugins.toolkit as tk
from ckan import model
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
        original_user_id = session.get("lmi_impostor_user_id")

        active_session = ImpostorSession.get(original_user_id, tk.current_user.id)

        if not active_session:
            return

        if active_session.expires < time.time() or not active_session.active:
            tk.logout_user()
            tk.login_user(active_session.user)

            session.pop("lmi_impostor_user_id", None)
            session.pop("lmi_impostor_expires", None)

            active_session.expire()

            tk.h.flash_success(tk._("You have been logged out of burrowed identity."))
