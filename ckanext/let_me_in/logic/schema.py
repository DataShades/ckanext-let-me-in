from __future__ import annotations

from typing import Any

from ckan import types
from ckan.logic.schema import validator_args

Schema = dict[str, Any]


@validator_args
def lmi_generate_otl(  # noqa: PLR0913
    ignore_missing: types.Validator,
    unicode_safe: types.Validator,
    user_id_exists: types.Validator,
    user_name_exists: types.Validator,
    user_email_exists: types.Validator,
    int_validator: types.Validator,
    is_positive_integer: types.Validator,
) -> types.Schema:
    return {
        "uid": [ignore_missing, unicode_safe, user_id_exists],
        "name": [ignore_missing, unicode_safe, user_name_exists],
        "mail": [ignore_missing, unicode_safe, user_email_exists],
        "ttl": [ignore_missing, int_validator, is_positive_integer],
    }
