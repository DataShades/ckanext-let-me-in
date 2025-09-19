from __future__ import annotations

import pytest

import ckan.plugins.toolkit as tk

from ckanext.let_me_in.logic.validators import user_email_exists


class TestEmailExistValidator:
    def test_no_user(self):
        with pytest.raises(tk.Invalid, match="Not found: User"):
            user_email_exists("test", {})

    @pytest.mark.usefixtures("clean_db")
    def test_user_exists(self, user):
        assert user_email_exists(user["email"], {})
