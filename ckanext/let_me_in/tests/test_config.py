from __future__ import annotations

import pytest

import ckanext.let_me_in.config as lmi_config


@pytest.mark.usefixtures("with_plugins")
class TestOTLConfig:
    @pytest.mark.ckan_config(lmi_config.CONF_OTL_LINK_TTL, 999)
    def test_set_default_ttl(self):
        assert lmi_config.get_default_otl_link_ttl() == 999

    def test_default_ttl(self):
        assert lmi_config.get_default_otl_link_ttl() == lmi_config.DEFAULT_OTL_LINK_TTL
