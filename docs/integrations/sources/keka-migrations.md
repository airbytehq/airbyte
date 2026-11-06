import MigrationGuide from '@site/static/_migration_guides_upgrade_guide.md';

# Keka Migration Guide

## Upgrading to 0.1.0

### What changed

The connector now requires a `subdomain` setting and sends API requests to
`https://<subdomain>.keka.com/api/v1`. Pagination starts at page 1, and the network
allowlist includes the authentication host, `login.keka.com`.

### Why this changed

Earlier versions hard-coded `master.keka.com` for every company. Keka's current
[API reference](https://developers.keka.com/reference/get_hris-employees) specifies
a company-specific hostname. The correct company cannot be inferred from the
existing connector configuration, so it must be supplied explicitly.

### Who is affected

All Keka sources upgrading from versions earlier than 0.1.0 must provide their
company subdomain. Stream names, schemas, and sync modes are unchanged.

Upgrade and configure the subdomain by October 22, 2026. Connections still using
the old version will be disabled at the deadline rather than automatically
upgraded without the required configuration.

### Required steps

1. Find your company's Keka URL. For `https://acme.keka.com`, the subdomain is `acme`.
2. Upgrade the connector to 0.1.0.
3. Before running a sync, edit the source configuration and enter the **Company
   Subdomain** without the protocol or `.keka.com` suffix. If your actual company
   URL is `https://master.keka.com`, enter `master` explicitly.
4. Keep your existing client ID, client secret, and API key. Set both **Grant Type**
   and **Scope** to `kekaapi`, then save and test the connection.
5. Resume syncs. No stream reset is required for this upgrade.

## Connector upgrade guide

<MigrationGuide />
