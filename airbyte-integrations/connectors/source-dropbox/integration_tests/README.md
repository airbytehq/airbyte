# Source Dropbox acceptance fixtures

Connector acceptance tests require an uncommitted `secrets/config.json` with
valid Dropbox credentials. The configured account should expose a stable test
folder containing at least one file and one subfolder beneath the configured
`path`.

The credentials need these scopes for the committed acceptance catalogs:

- `account_info.read`
- `files.metadata.read`

The full-refresh catalog selects `files` and `folders`. The incremental catalog
selects only `entries`, whose opaque Dropbox cursor is connector state and is
not a record field.

The committed `invalid_config.json` contains no real credential. Do not commit
`secrets/config.json`, access tokens, refresh tokens, authorization codes, or
real Dropbox test data.

Sharing streams, Dropbox Business contexts, and File Properties are covered by
unit tests. Future upstream CI can expand acceptance coverage after a suitable
Dropbox sandbox and Airbyte secret are provisioned.
