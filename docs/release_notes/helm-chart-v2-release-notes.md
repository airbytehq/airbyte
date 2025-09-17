# V2 Helm Chart Release Notes

This page documents changes to user-configurable values in the Airbyte V2 Helm Chart across versions. **These release notes only apply to users deploying Airbyte using Helm Chart V2.** If you are still using the V1 Helm Chart, these changes do not affect your deployment.

For users migrating from V1 to V2, please refer to the migration guides:
- [Self-Managed Community V2 Migration Guide](../platform/deploying-airbyte/chart-v2-community.mdx)
- [Self-Managed Enterprise V2 Migration Guide](../platform/enterprise-setup/chart-v2-enterprise.mdx)

These release notes focus on configuration options that users can modify when deploying Airbyte with the V2 Helm Chart.

## Version 2.0.12

### Added
- `auth.internalApi: {}` - New internal API authentication configuration

### Removed
- **Manifest Runner Component**: Complete removal of `manifestRunner.*` configuration section
  - All manifest runner deployment, ingress, and security configurations have been removed
  - **Migration**: Remove any `manifestRunner.*` configurations from your values.yaml file

### Changed
- **Connector Registry**: `connectorRegistry.seedProvider` changed from `"remote"` to `"local"`
  - **Migration**: No action required - this change improves reliability by using local connector definitions
- **Update Definitions Job**: `cron.jobs.updateDefinitions.enabled` changed from `true` to `false`
  - **Migration**: If you rely on automatic connector definition updates, set `cron.jobs.updateDefinitions.enabled: true` in your values.yaml
- **Google Secret Manager**: Removed `storage.googleSecretManager.region` configuration option
  - **Migration**: Remove the `region` field from your Google Secret Manager configuration if present

## Version 2.0.11

No user-configurable changes in this version.

## Version 2.0.10

No user-configurable changes in this version.

## Version 2.0.9

### Added
- **AWS Configuration**: New `global.aws.assumeRole.*` section for AWS role assumption
  - `global.aws.assumeRole.accessKeyId`
  - `global.aws.assumeRole.accessKeyIdSecretKey`
  - `global.aws.assumeRole.secretAcessKey`
  - `global.aws.assumeRole.secretAccessKeySecretKey`
- **Cloud SQL Proxy**: New `global.cloudSqlProxy.enabled` configuration

### Changed
- **API Configuration**: Simplified `global.api` from `authHeaderName: X-Airbyte-Auth` to empty object `{}`
  - **Migration**: Remove `global.api.authHeaderName` from your values.yaml if present
- **Database Port**: Fixed formatting consistency in database port configuration

## Version 2.0.8

No user-configurable changes in this version.

## Version 2.0.7

No user-configurable changes in this version.

## Version 2.0.6

### Changed
- **Database Configuration**: `global.database.database` renamed to `global.database.name`
  - **Migration**: Update your values.yaml to use `global.database.name` instead of `global.database.database`

## Version 2.0.5

No user-configurable changes in this version.

## Version 2.0.4

No user-configurable changes in this version.

## Version 2.0.3

### Added
- **Audit Logging**: New `storage.bucket.auditLogging` configuration for audit log storage
- **Webapp Analytics Configuration**: Complete new section `webapp.*` with analytics and monitoring integrations:
  - `webapp.datadogApplicationId`
  - `webapp.datadogClientToken`
  - `webapp.datadogEnv`
  - `webapp.datadogService`
  - `webapp.datadogSite`
  - `webapp.hockeystackApiKey`
  - `webapp.launchdarklyKey`
  - `webapp.osanoKey`
  - `webapp.segmentToken`
  - `webapp.zendeskKey`
- **Worker Configuration Enhancements**:
  - `worker.maxCheckWorkers`
  - `worker.maxSyncWorkers`

### Removed
- **Cloud API**: Removed `global.cloudApi.url` configuration
  - **Migration**: Remove `global.cloudApi.url` from your values.yaml if present
- **Connector Builder Server**: Removed `webapp.connectorBuilderServer.url` configuration
  - **Migration**: Remove `webapp.connectorBuilderServer.url` from your values.yaml if present
- **Worker Limits**: Removed hardcoded `maxNotifyWorkers: 5` from multiple worker components
  - **Migration**: If you need to set worker limits, use the new configurable worker options

### Changed
- **Temporal Version**: Updated from `"1.23.0"` to `"1.27.2"`
  - **Migration**: No action required - this is an internal dependency update
- **Database Engine**: Changed from `"postgresql"` to `"postgres12"`
  - **Migration**: Update your database engine configuration if you're using external databases
- **Worker Configuration**: Changed `maxNotifyWorkers` from hardcoded `5` to configurable empty string
  - **Migration**: Set explicit worker limits in your values.yaml if needed

## Version 2.0.2

No user-configurable changes in this version.

## Version 2.0.1

No user-configurable changes in this version.

## Version 2.0.0

Initial release of the V2 Helm Chart with comprehensive user-configurable options including:
- Global configuration settings
- Authentication and security framework
- Database and storage configurations
- Worker and deployment settings
- Monitoring and observability options

**Migration from V1**: See the [V2 Migration Guide](../platform/deploying-airbyte/chart-v2-community.mdx) for complete migration instructions from V1 to V2 charts.
