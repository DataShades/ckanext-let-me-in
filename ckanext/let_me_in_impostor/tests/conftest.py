import time
from collections.abc import Callable
from typing import Any

import pytest
from pytest_factoryboy import register

from ckan.plugins import load_all
from ckan.tests import factories

from ckanext.let_me_in.config import get_impostor_ttl
from ckanext.let_me_in_impostor.model import ImpostorSession


@pytest.fixture
def impostor_session(user_factory: Callable[..., dict[str, Any]]) -> ImpostorSession:
    user = user_factory()
    target_user = user_factory()

    return ImpostorSession.create(
        user_id=user["id"],
        target_user_id=target_user["id"],
        expires=int(time.time() + get_impostor_ttl()),
    )


@pytest.fixture
def impostor_session_factory(
    user_factory: Callable[..., dict[str, Any]],
) -> Callable[..., ImpostorSession]:
    def _factory(**kwargs: Any) -> ImpostorSession:
        user_id = kwargs.pop("user_id", user_factory()["id"])
        target_user_id = kwargs.pop("target_user_id", user_factory()["id"])
        expires = kwargs.pop("expires", get_impostor_ttl())

        return ImpostorSession.create(
            user_id=user_id,
            target_user_id=target_user_id,
            expires=int(time.time() + expires),
        )

    return _factory


@pytest.fixture(scope="session")
def reset_db_once(reset_db: Callable[..., Any], migrate_db_for: Callable[..., Any]) -> None:
    """Internal fixture that cleans DB only the first time it's used."""
    load_all()
    reset_db()

    migrate_db_for("let_me_in_impostor")


@register(_name="user")
class UserFactory(factories.UserWithToken):
    pass


@register(_name="sysadmin")
class SysadminFactory(factories.SysadminWithToken):
    pass
