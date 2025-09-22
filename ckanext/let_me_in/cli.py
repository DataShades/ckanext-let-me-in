from __future__ import annotations

import logging

import click

import ckan.plugins.toolkit as tk

from ckanext.let_me_in.config import get_default_otl_link_ttl

logger = logging.getLogger(__name__)

__all__ = [
    "letmein",
]


@click.group(short_help="Let me in!")
def letmein():
    pass


@letmein.command()
@click.option("--uid", "-n", default=None, help="User ID")
@click.option("--name", "-u", default=None, help="User name")
@click.option("--mail", "-e", default=None, help="User email")
@click.option("--ttl", "-t", default=None, type=int, help="Link time-to-live in seconds")
def uli(uid: str, name: str, mail: str, ttl: int):
    """Create a one-time login link for a user by its ID/name/email."""
    try:
        result = tk.get_action("lmi_generate_otl")(
            {"ignore_auth": True},
            {
                "uid": uid,
                "name": name,
                "mail": mail,
                "ttl": ttl or get_default_otl_link_ttl(),
            },
        )
    except tk.ValidationError as e:
        return click.secho(e.error_dict, fg="red", err=True)

    click.echo("A one-time login link has been generated")
    click.secho(result["url"], fg="green")
