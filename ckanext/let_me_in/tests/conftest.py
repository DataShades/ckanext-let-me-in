from collections.abc import Callable
from typing import Any

import pytest

from ckan.plugins import load_all


@pytest.fixture(scope="session")
def reset_db_once(reset_db: Callable[..., Any], migrate_db_for: Callable[..., Any]) -> None:
    """Internal fixture that cleans DB only the first time it's used."""
    load_all()
    reset_db()

    migrate_db_for("let_me_in_impostor")
