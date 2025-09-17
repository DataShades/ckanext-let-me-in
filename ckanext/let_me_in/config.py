import ckan.plugins.toolkit as tk

CONF_OTL_LINK_TTL = "ckanext.let_me_in.otl_link_ttl"
DEFAULT_OTL_LINK_TTL = 86400

CONF_IMPOSTOR_TTL = "ckanext.let_me_in.impostor.ttl"
DEFAULT_IMPOSTOR_TTL = 900

CONF_SHOW_TOOLBAR_BUTTON = "ckanext.let_me_in.impostor.show_toolbar_button"
DEFAULT_SHOW_TOOLBAR_BUTTON = True

CONF_ACTIVITY_PER_PAGE = "ckanext.let_me_in.impostor.activity_per_page"
DEF_ACTIVITY_PER_PAGE = 10


def get_default_otl_link_ttl() -> int:
    """Return a default TTL for an OTL link in seconds."""
    return tk.asint(tk.config.get(CONF_OTL_LINK_TTL, DEFAULT_OTL_LINK_TTL))


def get_impostor_ttl() -> int:
    """Return a default TTL for an Impostor session in seconds."""
    return tk.asint(tk.config.get(CONF_IMPOSTOR_TTL, DEFAULT_IMPOSTOR_TTL))


def get_show_toolbar_button() -> bool:
    """Return whether to show the Impostor link in the toolbar for sysadmins."""
    return tk.asbool(
        tk.config.get(CONF_SHOW_TOOLBAR_BUTTON, DEFAULT_SHOW_TOOLBAR_BUTTON)
    )


def get_impostor_activity_per_page() -> int:
    """Return the number of Impostor activities to show per page."""
    return tk.asint(tk.config.get(CONF_ACTIVITY_PER_PAGE, DEF_ACTIVITY_PER_PAGE))
