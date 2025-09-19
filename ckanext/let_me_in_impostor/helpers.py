import ckan.plugins.toolkit as tk
from ckan import model
from ckan.common import session

import ckanext.let_me_in.config as lmi_config


def lmi_get_active_users_options() -> list[dict[str, str]]:
    """Return a list of active users options, excluding the current user."""
    current_user_id = tk.current_user.id if tk.current_user else ""

    result = (
        model.Session.query(model.User)
        .filter(model.User.state == model.State.ACTIVE)
        .filter(model.User.email.isnot(None))
        .filter(model.User.id != current_user_id)
        .all()
    )

    return [{"value": user.id, "text": f"{user.display_name} ({user.email})"} for user in result]


def lmi_is_current_user_an_impostor():
    """Check if the current user is an impostor."""
    return session.get("lmi_impostor_session_id") is not None


def lmi_show_toolbar_button() -> bool:
    """Return whether to show the Impostor link in the toolbar for sysadmins."""
    return lmi_config.get_show_toolbar_button()


def lmi_get_session_records_per_page() -> int:
    """Return the number of session records to show per page."""
    return lmi_config.get_session_records_per_page()


def lmi_get_default_otl_link_ttl() -> int:
    """Return the default TTL for one-time login links."""
    return lmi_config.get_default_otl_link_ttl()
