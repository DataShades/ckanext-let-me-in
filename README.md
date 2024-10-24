[![Tests](https://github.com/DataShades/ckanext-let-me-in/actions/workflows/test.yml/badge.svg?branch=master)](https://github.com/DataShades/ckanext-let-me-in/actions/workflows/test.yml)

# ckanext-let-me-in

An extension that generates a one-time login link for a user by its `id`, `name` or `email`.

Use `lmi_generate_otl` API action or `ckan letmein uli` CLI command to generate an OTL link.

The link will expire in 24h, by default or after it was used.

## Requirements

Compatibility with core CKAN versions:

| CKAN version    | Compatible? |
| --------------- | ----------- |
| 2.8 and earlier | no          |
| 2.9             | not yet     |
| 2.10+           | yes         |

## Installation

1. Use `pip` to install an extension: `pip install ckanext-let-me-in`
2. Add `let_me_in` to the `ckan.plugins` setting in your CKAN config file.

## Config settings

Available configuration options:

    # The number in seconds that specifies the OTL link TTL (optional, default: 86400).
	ckanext.let_me_in.otl_link_ttl= 3600

## Developer installation

To install ckanext-let-me-in for development, activate your CKAN virtualenv and
do:

    git clone https://github.com/DataShades/ckanext-let-me-in.git
    cd ckanext-let-me-in
    python setup.py develop

## Tests

To run the tests, do:

    pytest --ckan-ini=test.ini

## License

[AGPL](https://www.gnu.org/licenses/agpl-3.0.en.html)
