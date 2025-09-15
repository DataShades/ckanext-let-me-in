from __future__ import annotations

from typing import Any

import pytest

import ckan.model as model
import ckan.plugins as p
from ckan.tests.helpers import call_action

from ckanext.let_me_in.interfaces import ILetMeIn


class TestOTLPlugin(p.SingletonPlugin):
    p.implements(p.IConfigurable, inherit=True)
    p.implements(ILetMeIn)

    def configure(self, _config):
        self.manage_user_call = 0
        self.before_otl_login_call = 0
        self.after_otl_login_call = 0

    def manage_user(self, user: model.User, context: dict[str, Any]) -> model.User:
        self.manage_user_call += 1

        return user

    def before_otl_login(self, user: model.User, context: dict[str, Any]) -> None:
        self.before_otl_login_call += 1

    def after_otl_login(self, user: model.User, context: dict[str, Any]) -> None:
        self.after_otl_login_call += 1


@pytest.mark.ckan_config("ckan.plugins", "let_me_in test_otl_plugin")
@pytest.mark.usefixtures("non_clean_db", "with_plugins")
class TestOTLInterace:
    def test_xxx(self, app, user, sysadmin):
        result = call_action("lmi_generate_otl", uid=user["id"])

        result = app.get(result["url"], status=200)

        manage_user_call_total = sum(
            plugin.manage_user_call
            for plugin in p.PluginImplementations(ILetMeIn)
            if plugin.name == "test_otl_plugin"
        )

        before_otl_login_call_total = sum(
            plugin.before_otl_login_call
            for plugin in p.PluginImplementations(ILetMeIn)
            if plugin.name == "test_otl_plugin"
        )

        after_otl_login_call_total = sum(
            plugin.after_otl_login_call
            for plugin in p.PluginImplementations(ILetMeIn)
            if plugin.name == "test_otl_plugin"
        )

        assert manage_user_call_total == 1
        assert before_otl_login_call_total == 1
        assert after_otl_login_call_total == 1
