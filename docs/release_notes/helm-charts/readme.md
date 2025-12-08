---
products: oss-*
---

# Helm chart change log

This page documents changes to configurable values in Airbyte Helm charts starting with version 2.0.0.

**In most cases, you don't need to take any action** as a result of the information on this page. Airbyte adds, removes, and changes configurations while developing capabilities and making internal architectural changes and this doesn't affect you. Monitor Airbyte's [platform release notes](../) and [breaking change list](../breaking-changes) instead. These pages notify you when new features are available or you need to take specific upgrade actions.

This information is only relevant if you deploy Airbyte using Helm chart V2. If you're still using the V1 Helm chart, ignore this page.

<!-- SEE END OF FILE FOR INSTRUCTIONS ON HOW TO UPDATE THIS CHANGELOG -->

<!-- vale off -->

## Version 2.0.19

No configurable changes in this version.

## Version 2.0.18

### Added

- **Management Ports**: New `management.port` configuration options for multiple components
  - `airbyteBootloader.management.port`
  - `connectorBuilderServer.management.port`
  - `connectorRolloutWorker.management.port`
  - `cron.management.port`
  - `featureflagServer.management.port`
  - `metrics.management.port`
  - `server.management.port`
  - `stiggSidecar.management.port`
  - `temporalUi.management.port`
  - `worker.management.port`
  - `workloadApiServer.management.port`
  - `workloadLauncher.management.port`

- **Debug Configuration**: New debug settings for multiple components
  - `airbyteBootloader.debug.enabled` and `airbyteBootloader.debug.remoteDebugPort`
  - `cron.debug.enabled` and `cron.debug.remoteDebugPort`
  - `metrics.debug.enabled` and `metrics.debug.remoteDebugPort`
  - `stiggSidecar.debug.enabled` and `stiggSidecar.debug.remoteDebugPort`

- **Stigg Integration**: New Stigg configuration options
  - `global.stigg.apiKeySecretKey`
  - `global.stigg.secretName`

- **Manifest Server Component**: New `manifestServer.*` configuration section
  - Complete deployment configuration including security context, probes, and ingress

- **Stigg Sidecar Component**: New `stiggSidecar.*` configuration section
  - Complete sidecar configuration including deployment, security, and resource settings

- **Ingress Configuration**: New top-level ingress options
  - `ingress.className`
  - `ingress.enabled`

- **Container Orchestrator**: New `global.workloads.containerOrchestrator.secretMountPath` configuration

### Changed

- **Connector Registry**: `global.connectorRegistry.seedProvider` changed from `"local"` to `"remote"`

- **Update Definitions Job**: `cron.jobs.updateDefinitions.enabled` changed from `false` to `true`

## Version 2.0.17

No configurable changes in this version.

## Version 2.0.16

No configurable changes in this version.

## Version 2.0.15

### Removed

- **Manifest Server Component**: Complete removal of `manifestServer.*` configuration section
  - All manifest server deployment, ingress, and security configurations have been removed

- **Stigg Sidecar Component**: Complete removal of `stiggSidecar.*` configuration section
  - All Stigg sidecar deployment and configuration options have been removed

- **Stigg Configuration**: Removed Stigg-related global configurations
  - `global.stigg.apiKeySecretKey`
  - `global.stigg.secretName`

- **Container Orchestrator**: Removed `global.workloads.containerOrchestrator.secretMountPath` configuration

### Changed

- **Authentication**: `global.auth.enabled` changed from `true` to `false`

- **Connector Registry**: `global.connectorRegistry.seedProvider` changed from `"remote"` to `"local"`

- **Update Definitions Job**: `cron.jobs.updateDefinitions.enabled` changed from `true` to `false`

## Version 2.0.14

### Changed

- **Authentication**: `global.auth.enabled` changed from `false` to `true`

- **Manifest Server**: `manifestServer.image.tag` updated from `"7.0.4"` to `"7.2.0"`

## Version 2.0.13

### Added

- **Manifest Server Component**: New `manifestServer.*` configuration section
  - Complete deployment configuration including replicas, security context, probes, and ingress

- **Stigg Sidecar Component**: New `stiggSidecar.*` configuration section
  - Complete sidecar configuration including deployment, security, and resource settings

- **Stigg Configuration**: New Stigg-related global configurations
  - `global.stigg.apiKeySecretKey`
  - `global.stigg.secretName`

- **Container Orchestrator**: New `global.workloads.containerOrchestrator.secretMountPath` configuration

### Changed

- **Connector Registry**: `global.connectorRegistry.seedProvider` changed from `"local"` to `"remote"`

- **Update Definitions Job**: `cron.jobs.updateDefinitions.enabled` changed from `false` to `true`

## Version 2.0.12

### Removed

- **Manifest Server Component**: Complete removal of `manifestServer.*` configuration section
  - All manifest server deployment, ingress, and security configurations have been removed

- **Stigg Sidecar Component**: Complete removal of `stiggSidecar.*` configuration section
  - All Stigg sidecar deployment and configuration options have been removed

- **Stigg Configuration**: Removed Stigg-related global configurations
  - `global.stigg.apiKeySecretKey`
  - `global.stigg.secretName`

- **Container Orchestrator**: Removed `global.workloads.containerOrchestrator.secretMountPath` configuration

### Changed

- **Connector Registry**: `global.connectorRegistry.seedProvider` changed from `"remote"` to `"local"`

- **Update Definitions Job**: `cron.jobs.updateDefinitions.enabled` changed from `true` to `false`

## Version 2.0.11

### Removed

- **Manifest Runner Component**: Complete removal of `manifestRunner.*` configuration section
  - All manifest runner deployment, ingress, and security configurations have been removed

### Added

- **Manifest Server Component**: New `manifestServer.*` configuration section (replacing manifestRunner)
  - Complete deployment configuration including replicas, security context, probes, and ingress

- **Stigg Sidecar Component**: New `stiggSidecar.*` configuration section
  - Complete sidecar configuration including deployment, security, and resource settings

- **Stigg Configuration**: New Stigg-related global configurations
  - `global.stigg.apiKeySecretKey`
  - `global.stigg.secretName`

- **Container Orchestrator**: New `global.workloads.containerOrchestrator.secretMountPath` configuration

## Version 2.0.10

No configurable changes in this version.

## Version 2.0.9

### Added

- **Manifest Runner Component**: New `manifestRunner.*` configuration section
  - Complete deployment configuration including replicas, security context, probes, and ingress

## Version 2.0.8

### Removed

- **API Configuration**: Removed `global.api.authHeaderName` configuration

### Added

- **Declarative Sources Updater**: New `cron.jobs.declarativeSourcesUpdater.enabled` configuration

- **Micronaut Environment**: New `global.micronaut.environments.0` configuration

- **Server Configuration**: New server-specific options
  - `server.ioExecutor.numThreads`
  - `server.webapp.posthogApiKey`
  - `server.webapp.posthogHost`

### Changed

- **Connector Registry**: `global.connectorRegistry.seedProvider` changed from `"local"` to `"remote"`

- **Update Definitions Job**: `cron.jobs.updateDefinitions.enabled` changed from `false` to `true`

- **Webapp**: `webapp.enabled` changed from `true` to `false`

## Version 2.0.7

### Removed

- **Server Applications**: Removed `server.applications` configuration

### Added

- **GitHub Token Configuration**: New GitHub token options for connector builder and rollout worker
  - `connectorBuilderServer.githubToken` and `connectorBuilderServer.githubTokenSecretKey`
  - `connectorRolloutWorker.githubToken` and `connectorRolloutWorker.githubTokenSecretKey`

- **AWS Configuration**: New AWS role assumption options
  - `global.aws.assumeRole.accessKeyId`
  - `global.aws.assumeRole.accessKeyIdSecretKey`
  - `global.aws.assumeRole.secretAccessKeySecretKey`
  - `global.aws.assumeRole.secretAcessKey`

- **Cloud SQL Proxy**: New `global.cloudSqlProxy.enabled` configuration

- **Server Component**: Expanded `server.*` configuration section with additional options

## Version 2.0.6

### Removed

- **GitHub Token Configuration**: Removed GitHub token options
  - `connectorBuilderServer.githubToken` and `connectorBuilderServer.githubTokenSecretKey`
  - `connectorRolloutWorker.githubToken` and `connectorRolloutWorker.githubTokenSecretKey`

- **AWS Configuration**: Removed AWS role assumption options
  - `global.aws.assumeRole.*` (all sub-keys)

- **Cloud SQL Proxy**: Removed `global.cloudSqlProxy.enabled` configuration

- **Server Configuration**: Removed multiple server-specific options
  - `server.auditLoggingEnabled`
  - `server.configDbMaxPoolSize`
  - `server.connectorDatadogSupportNames`
  - `server.httpIdleTimeout`
  - `server.openai.syncAssistantApiKey` and `server.openai.syncAssistantApiKeySecretKey`
  - `server.publicApiExecutor.numThreads`
  - `server.scheduler.numThreads`
  - `server.warehouseExports.bucketName` and `server.warehouseExports.projectId`

### Added

- **Server Applications**: New `server.applications` configuration

## Version 2.0.5

No configurable changes in this version.

## Version 2.0.4

### Removed

- **Database Configuration**: Removed `global.database.database` configuration (renamed to `global.database.name`)

- **Server Applications**: Removed `server.applications` configuration

### Added

- **Database Configuration**: New `global.database.name` configuration (replaces `global.database.database`)

- **GitHub Token Configuration**: New GitHub token options for connector builder and rollout worker
  - `connectorBuilderServer.githubToken` and `connectorBuilderServer.githubTokenSecretKey`
  - `connectorRolloutWorker.githubToken` and `connectorRolloutWorker.githubTokenSecretKey`

- **AWS Configuration**: New AWS role assumption options
  - `global.aws.assumeRole.accessKeyId`
  - `global.aws.assumeRole.accessKeyIdSecretKey`
  - `global.aws.assumeRole.secretAccessKeySecretKey`
  - `global.aws.assumeRole.secretAcessKey`

- **Cloud SQL Proxy**: New `global.cloudSqlProxy.enabled` configuration

- **Server Configuration**: New server-specific options
  - `server.auditLoggingEnabled`
  - `server.configDbMaxPoolSize`
  - `server.connectorDatadogSupportNames`
  - `server.httpIdleTimeout`
  - `server.openai.syncAssistantApiKey` and `server.openai.syncAssistantApiKeySecretKey`
  - `server.publicApiExecutor.numThreads`
  - `server.scheduler.numThreads`
  - `server.warehouseExports.bucketName` and `server.warehouseExports.projectId`

## Version 2.0.3

### Added

- **Webapp Analytics Configuration**: New analytics and monitoring integrations
  - `server.webapp.datadogApplicationId`
  - `server.webapp.datadogClientToken`
  - `server.webapp.datadogEnv`
  - `server.webapp.datadogService`
  - `server.webapp.datadogSite`
  - `server.webapp.hockeystackApiKey`
  - `server.webapp.launchdarklyKey`
  - `server.webapp.osanoKey`
  - `server.webapp.segmentToken`
  - `server.webapp.zendeskKey`

## Version 2.0.2

### Added

- **Audit Logging**: New `global.storage.bucket.auditLogging` configuration

## Version 2.0.1

### Removed

- **Cloud API**: Removed `global.cloudApi.url` configuration

- **Connector Builder Server URL**: Removed `webapp.connectorBuilderServer.url` configuration

- **Worker Limits**: Removed hardcoded `maxNotifyWorkers` from multiple worker components
  - `connectorRolloutWorker.maxNotifyWorkers`
  - `workloadLauncher.maxNotifyWorkers`

### Added

- **Worker Configuration**: New worker limit options
  - `worker.maxCheckWorkers`
  - `worker.maxSyncWorkers`

### Changed

- **Temporal Version**: `temporal.image.tag` updated from `"1.23.0"` to `"1.27.2"`

- **Database Engine**: `temporal.database.engine` changed from `"postgresql"` to `"postgres12"`

- **Worker Configuration**: `worker.maxNotifyWorkers` changed from `5` to `""` (empty string)

## Version 2.0.0

Initial release of the V2 Helm Chart with comprehensive user-configurable options including:

- Global configuration settings
- Authentication and security framework
- Database and storage configurations
- Worker and deployment settings
- Monitoring and observability options

**Migration from V1**: see the V2 Migration Guide for complete migration instructions from V1 to V2 charts.

<!-- vale on -->

<!-- 

-------------------------
HOW TO UPDATE THIS FILE
-------------------------

Anyone can compare a published Helm chart to the previous version to generate a change log. This is an excellent task to delegate to an AI, though you should run a manual spot check to ensure it hasn't "interpreted" the result.

## Overview

The changelog generation process compares `values.yaml` files between consecutive Helm chart versions published in the `airbytehq/charts` repository. By identifying Added, Removed, and Changed configuration keys, we can document user-facing changes and provide migration guidance.

## Prerequisites

Required tools:
- `helm` (v3+)
- `python3` (with PyYAML)
- Standard Unix tools: `sort`, `comm`, `awk`, `cut`

Install PyYAML if needed:
```bash
pip3 install pyyaml
```

## Setup: Create the Python Flattening Script

Create a file called `flatten_yaml.py`:

```python
#!/usr/bin/env python3
"""
Flatten a YAML file to dot-notation key-value pairs.
Usage: python3 flatten_yaml.py <input.yaml>
Output: TSV format with key\tvalue (JSON-encoded)
"""
import yaml
import json
import sys

def flatten_dict(d, parent_key='', sep='.'):
    """Recursively flatten a nested dictionary to dot-notation paths."""
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        elif isinstance(v, list):
            for i, item in enumerate(v):
                if isinstance(item, dict):
                    items.extend(flatten_dict(item, f"{new_key}.{i}", sep=sep).items())
                else:
                    items.append((f"{new_key}.{i}", item))
        else:
            items.append((new_key, v))
    return dict(items)

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python3 flatten_yaml.py <input.yaml>", file=sys.stderr)
        sys.exit(1)
    
    with open(sys.argv[1]) as f:
        data = yaml.safe_load(f)
        flat = flatten_dict(data)
        for k, v in sorted(flat.items()):
            print(f"{k}\t{json.dumps(v)}")
```

Make it executable:
```bash
chmod +x flatten_yaml.py
```

## Step-by-Step Process

### 1. Set Up Helm Repository

Add the V2 Helm chart repository:

```bash
helm repo add airbyte-v2 https://airbytehq.github.io/charts
helm repo update
```

### 2. List Available Chart Versions

Get all published chart versions:

```bash
# Human-readable list
helm search repo airbyte-v2/airbyte --versions

# Get sorted version list for scripting
helm search repo airbyte-v2/airbyte --versions | awk 'NR>1 {print $2}' | sort -V > versions.txt
```

### 3. Create Working Directory Structure

```bash
mkdir -p out/values out/maps out/keys out/diff
```

### 4. Extract values.yaml for Each Version

Extract values.yaml files for the versions you want to compare:

```bash
# Example: Extract values for versions 2.0.14 and 2.0.15
helm show values airbyte-v2/airbyte --version 2.0.14 > out/values/2.0.14.yaml
helm show values airbyte-v2/airbyte --version 2.0.15 > out/values/2.0.15.yaml
```

### 5. Flatten YAML to Key-Value Pairs

Convert nested YAML to flat "path=value" format:

```bash
# Flatten 2.0.14 values to TSV
python3 flatten_yaml.py out/values/2.0.14.yaml > out/maps/2.0.14.tsv

# Flatten 2.0.15 values to TSV
python3 flatten_yaml.py out/values/2.0.15.yaml > out/maps/2.0.15.tsv
```

Extract just the keys (configuration paths):

```bash
cut -f1 out/maps/2.0.14.tsv | sort -u > out/keys/2.0.14.txt
cut -f1 out/maps/2.0.15.tsv | sort -u > out/keys/2.0.15.txt
```

### 6. Compute Differences Between Versions

**Added keys** (present in 2.0.15, not in 2.0.14):

```bash
comm -13 out/keys/2.0.14.txt out/keys/2.0.15.txt > out/diff/2.0.14_to_2.0.15.added
```

**Removed keys** (present in 2.0.14, not in 2.0.15):

```bash
comm -23 out/keys/2.0.14.txt out/keys/2.0.15.txt > out/diff/2.0.14_to_2.0.15.removed
```

**Changed keys** (present in both, but value changed):

```bash
awk -F'\t' 'FNR==NR{a[$1]=$2; next} ($1 in a) && a[$1] != $2 {print $1"\t"a[$1]" -> "$2}' \
  out/maps/2.0.14.tsv out/maps/2.0.15.tsv > out/diff/2.0.14_to_2.0.15.changed
```

### 7. Analyze and Group Changes

Review the diff files to identify patterns:

```bash
# View added keys
cat out/diff/2.0.14_to_2.0.15.added

# View removed keys
cat out/diff/2.0.14_to_2.0.15.removed

# View changed keys with old -> new values
cat out/diff/2.0.14_to_2.0.15.changed
```

Group changes by component prefix:

```bash
# Count added keys by top-level component
cut -d'.' -f1 out/diff/2.0.14_to_2.0.15.added | sort | uniq -c

# Count removed keys by top-level component
cut -d'.' -f1 out/diff/2.0.14_to_2.0.15.removed | sort | uniq -c

# Count changed keys by top-level component
cut -d'.' -f1 out/diff/2.0.14_to_2.0.15.changed | sort | uniq -c
```

### 8. Format Changelog Entry

Create a changelog entry following this structure:

```markdown
## Version 2.0.15

### Removed

- **Component Name**: Description of what was removed
  - Specific configuration paths affected

### Added

- **Component Name**: Description of what was added
  - Specific configuration paths affected

### Changed

- **Configuration Name**: Description of the change (old value -> new value)
```

**Guidelines for formatting:**

1. **Group related changes** by component (e.g., `manifestServer.*`, `auth.*`, `global.*`)
2. **Use wildcards** for entire sections (e.g., "Complete removal of `manifestServer.*` configuration section")
3. **Avoid migration guidance** for every change: if users need to do a migration, explain that migration in the release notes and breaking changes for that version, not here.
4. **Mark internal changes** as "No action required" when appropriate (e.g., image tag updates)
5. **Note "No configurable changes"** if all three diff files are empty

-->
