from __future__ import annotations

from typing import Any

import ckan.plugins as p
import ckan.plugins.toolkit as tk
from ckan import model

import ckanext.let_me_in.utils as lmi_utils
from ckanext.let_me_in.interfaces import ILetMeIn


@tk.blanket.actions
@tk.blanket.cli
@tk.blanket.auth_functions
@tk.blanket.blueprints
@tk.blanket.validators
@tk.blanket.config_declarations
class LetMeInPlugin(p.SingletonPlugin):
    p.implements(ILetMeIn, inherit=True)

    # ILetMeIn

    def after_otl_login(self, user: model.User, context: dict[str, Any]) -> None:
        lmi_utils.update_user_last_active(user)

        tk.h.flash_success("You have been logged in.")
