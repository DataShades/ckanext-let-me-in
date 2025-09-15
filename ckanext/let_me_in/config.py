import ckan.plugins.toolkit as tk

CONF_OTL_LINK_TTL = "ckanext.let_me_in.otl_link_ttl"
DEFAULT_OTL_LINK_TTL = 86400

CONF_IMPOSTOR_TTL = "ckanext.let_me_in.impostor.ttl"
DEFAULT_IMPOSTOR_TTL = 900


def get_default_otl_link_ttl() -> int:
    """Return a default TTL for an OTL link in seconds."""
    return tk.asint(tk.config.get(CONF_OTL_LINK_TTL, DEFAULT_OTL_LINK_TTL))


def get_impostor_ttl() -> int:
    """Return a default TTL for an Impostor session in seconds."""
    return tk.asint(tk.config.get(CONF_IMPOSTOR_TTL, DEFAULT_IMPOSTOR_TTL))
