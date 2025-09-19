from __future__ import annotations

import pytest

import ckan.model as model
import ckan.plugins.toolkit as tk
from ckan.tests.helpers import call_auth


@pytest.mark.usefixtures("non_clean_db", "with_plugins")
class TestGenerateOTLAuth:
    def test_anon(self):
        with pytest.raises(tk.NotAuthorized):
            call_auth("lmi_generate_otl", context={"user": None, "model": model})

    @pytest.mark.usefixtures("clean_db")
    def test_regular_user(self, user):
        with pytest.raises(tk.NotAuthorized):
            call_auth("lmi_generate_otl", context={"user": user["name"], "model": model})

    @pytest.mark.usefixtures("clean_db")
    def test_sysadmin(self, sysadmin):
        call_auth("lmi_generate_otl", context={"user": sysadmin["name"], "model": model})
