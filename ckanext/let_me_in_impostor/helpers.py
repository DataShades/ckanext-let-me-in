import ckan.plugins.toolkit as tk
from ckan import model
from ckan.common import session

from ckanext.let_me_in_impostor.model import ImpostorSession


def lmi_get_active_users():
    """Return a list of active users, excluding the current user."""
    current_user_id = tk.current_user.id if tk.current_user else ""

    return (
        model.Session.query(model.User)
        .filter(model.User.state == model.State.ACTIVE)
        .filter(model.User.email.isnot(None))
        .filter(model.User.id != current_user_id)
        .all()
    )

def lmi_is_current_user_an_impostor():
    """Check if the current user is an impostor."""
    return session.get("lmi_impostor_user_id") is not None


def lmi_get_impostor_sessions(user_id: str):
    """Return a list of all impostor session for the given user."""
    if not tk.current_user:
        return []

    return ImpostorSession.list(user_id)
