from __future__ import annotations

from typing import Any

import ckan.plugins.toolkit as tk
from ckan import model, types


def user_email_exists(email: str, context: types.Context) -> Any:
    """Ensures that user with a specific email exists.

    Transform the email to user ID
    """
    result = model.User.by_email(email)

    if not result:
        raise tk.Invalid(tk._("Not found: User"))

    return result.id
