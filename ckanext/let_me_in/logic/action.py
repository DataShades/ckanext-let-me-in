from __future__ import annotations

from datetime import datetime as dt
from datetime import timedelta as td
from typing import cast

import jwt

import ckan.plugins.toolkit as tk
from ckan import model, types
from ckan.logic import validate

import ckanext.let_me_in.config as lmi_config
import ckanext.let_me_in.logic.schema as schema
import ckanext.let_me_in.utils as lmi_utils


@validate(schema.lmi_generate_otl)
def lmi_generate_otl(
    context: types.Context, data_dict: types.DataDict
) -> types.ActionResult.AnyDict:
    """Generate a one-time login link for a specified user.

    :param uid: user ID
    :type uid: str

    :param name: username
    :type name: str

    :param mail: user email
    :type mail: str

    :param ttl: TTL for OTL link in seconds
    :type ttl: int
    """
    tk.check_access("lmi_generate_otl", context, data_dict)

    uid: str = data_dict.get("uid", "")
    name: str = data_dict.get("name", "")
    mail: str = data_dict.get("mail", "")
    ttl: int = data_dict.get("ttl", lmi_config.get_default_otl_link_ttl())

    if not any([uid, name, mail]):
        raise tk.ValidationError(
            tk._(
                "Please, provide uid, name or mail option",
            )
        )

    if sum([1 for x in (uid, name, mail) if x]) > 1:
        raise tk.ValidationError(
            tk._(
                "One param could be used at a time: uid, name or mail",
            )
        )

    user = cast(model.User, lmi_utils.get_user(uid or name or mail))
    now = dt.utcnow()

    token = jwt.encode(
        {
            "user_id": user.id,
            "exp": now + td(seconds=ttl),
            "created_at": now.timestamp(),
        },
        lmi_utils.get_secret(True),
        algorithm="HS256",
    )

    return {"url": tk.url_for("lmi.login_with_token", token=token, _external=True)}
