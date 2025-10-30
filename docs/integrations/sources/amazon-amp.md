# Amazon AMP

## Overview

The Amazon AMP source syncs the AMP API. It supports full refresh sync.

## Getting started

### Requirements

- AWS IAM Access Key
- AWS IAM Secret Key
- AWS AMP Workspace ID
- AWS Region

### Setup guide

- [Create IAM Keys](https://aws.amazon.com/premiumsupport/knowledge-center/create-access-key/)
- [Create AMP Workspace](https://docs.aws.amazon.com/prometheus/latest/userguide/AMP-create-workspace.html)
- Populate AMP with some metrics and alert rules

### Supported Streams

This Source is capable of syncing the following endpoints:

- /api/v1/label/__name__/values
- /api/v1/rules

### Features

| Feature           | Supported?\(Yes/No\) | Notes |
| :---------------- | :------------------- | :---- |
| Full Refresh Sync | Yes                  |       |
| Incremental Sync  | No                   |       |
| Namespaces        | No                   |       |

### Output schema

This source will output two streams for the configured AMP Workspace:

1. RulesStream:
  - name
  - state
  - query
  - duration
  - keepFiringFor
  - system
  - severity
  - description
  - runbook
  - summary
  - health
  - lastError
  - type
  - lastEvaluation
  - evaluationTime
  - labels
  - annotations
  - alerts
2. MetricNames
  - metric_name

### Properties

Required properties are 'AMP Workspace ID', 'AWS Region', 'AWS IAM Access Key ID' and 'AWS IAM Secret Key' as noted in
**bold** below.

- **AMP Workspace ID** (STRING)
  - ID of the AMP workspace
- **AWS Region** (STRING)
  - AWS region where AMP is deployed
- **AWS IAM Access Key ID** (STRING)
  - The Access Key ID of the AWS IAM Role with AMP access
- **AWS IAM Secret Key** (STRING)
  - The Secret Key of the AWS IAM Role with AMP access

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                              | Subject                           |
| :------ | :--------- | :-------------------------------------------------------- | :-------------------------------- |
| 0.1.0   | 2025-09-23 | [\#0000](https://github.com/airbytehq/airbyte/pull/0000)  | Initial version                   |

</details>
