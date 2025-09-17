# LET ME IN!

[![Tests](https://github.com/DataShades/ckanext-let-me-in/actions/workflows/test.yml/badge.svg)](https://github.com/DataShades/ckanext-let-me-in/actions/workflows/test.yml)

A CKAN extension that provides secure one-time login functionality and optional admin impersonation capabilities.

## Overview

**ckanext-let-me-in** generates one-time login links (OTL) that allow users to access their accounts without passwords. The extension consists of two components:

- **Core plugin**: Generates secure one-time login links via API or CLI
- **Impostor subplugin**: Provides a web UI for sysadmins to login as other users

## Requirements

| CKAN Version | Compatibility |
|--------------|---------------|
| 2.8 and earlier | ❌ Not supported |
| 2.9 | ⚠️ Not tested |
| 2.10 | ✅ Supported |
| 2.11 | ✅ Supported |
| `master` | ⚠️ Not tested |

## Installation

### Standard Installation

```bash
pip install ckanext-let-me-in
```

### Developer Installation

```bash
git clone https://github.com/DataShades/ckanext-let-me-in.git
cd ckanext-let-me-in
pip install -e .
```

## One-Time Login Links

This plugin allows generating secure one-time login links for users, which can be used to access their accounts without needing a password.

### Features

- Generate secure one-time login links for any user by ID, username, or email
- Multiple access methods: API endpoint and CLI command
- Configurable expiration (default: 24 hours)
- Links expire after first use or TTL timeout
- Secure token generation and validation

### Configuration

Add the plugin to your CKAN configuration:

```ini
ckan.plugins = let_me_in
```

### Configuration Options

| Setting | Description | Default | Example |
|---------|-------------|---------|---------|
| `ckanext.let_me_in.otl_link_ttl` | Time in seconds that OTL links remain valid | `86400` (24 hours) | `3600` (1 hour) |

### Usage

#### API Usage

Use the `lmi_generate_otl` action to generate links programmatically:

```python
result = tk.get_action('lmi_generate_otl')(
    context,
    {'uid': 'rsmith', 'ttl': 3600}  # Optional TTL override
)
```

#### CLI Usage

Generate links from the command line:

```bash
ckan letmein uli --name=rsmith
ckan letmein uli --mail=rsmith@ckan.example.com
ckan letmein uli --uid=0daa9f1d-671a-49f3-a7a6-15f4a263ef49 --ttl=3600
```

## Impostor Subplugin

This optional subplugin allows system administrators to impersonate other users via a web interface for a limited time.

> [!WARNING]
> This feature is not intended for use in a production environment. It should be used only for testing and troubleshooting.

### Features

- Web-based interface for system administrators
- Login as any user directly from admin panel or user profile pages
- Easy switch back to original admin account
- Visual indicators when impersonating users

### Configuration

Enable both plugins in your CKAN configuration:

```ini
ckan.plugins = let_me_in let_me_in_impostor
```

### Configuration Options

| Setting | Description | Default | Example |
|---------|-------------|---------|---------|
| `ckanext.let_me_in.impostor.ttl` | Impostor session timeout in seconds | `900` (15 minutes) | `7200` (2 hours) |
| `ckanext.let_me_in.impostor.show_toolbar_button` | Show a link to the Impostor interface in the toolbar for sysadmins | `true` | `false` |

### Usage

1. **Access the feature**: System administrators will see "Login as this user" buttons in:
   - User management pages in the admin panel
   - Individual user profile pages

2. **Impersonate a user**: Click the button to instantly login as that user without requiring their password

3. **Return to admin account**: Use the provided interface to switch back to your original administrator account at any time

### Security Notes

- Only system administrators can access impersonation features
- All impersonation activities will be logged for audit purposes
- Impostor sessions have configurable timeouts for added security

## Testing

Run the test suite:

```bash
pytest --ckan-ini=test.ini
```

## License

[AGPL](https://www.gnu.org/licenses/agpl-3.0.en.html)
