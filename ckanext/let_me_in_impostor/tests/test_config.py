from __future__ import annotations

import pytest

import ckanext.let_me_in.config as lmi_config


@pytest.mark.usefixtures("with_plugins")
class TestOTLImpostorConfig:
    def test_impostor_ttl_default(self):
        assert lmi_config.get_impostor_ttl() == lmi_config.DEFAULT_IMPOSTOR_TTL

    @pytest.mark.ckan_config(lmi_config.CONF_IMPOSTOR_TTL, 999)
    def test_set_impostor_ttl(self):
        assert lmi_config.get_impostor_ttl() == 999

    def test_show_toolbar_button_default(self):
        assert lmi_config.get_show_toolbar_button() is True

    @pytest.mark.ckan_config(lmi_config.CONF_SHOW_TOOLBAR_BUTTON, "false")
    def test_set_show_toolbar_button(self):
        assert lmi_config.get_show_toolbar_button() is False

    def test_session_records_per_page_default(self):
        assert lmi_config.get_session_records_per_page() == lmi_config.DEFAULT_SESSION_RECORDS_PER_PAGE

    @pytest.mark.ckan_config(lmi_config.CONF_SESSION_RECORDS_PER_PAGE, 50)
    def test_set_session_records_per_page(self):
        assert lmi_config.get_session_records_per_page() == 50
