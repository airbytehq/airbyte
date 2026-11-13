---
products: cloud
---

import AirbyteCloudIps from '@site/static/_airbyte_cloud_ips.md';

# IP allow list for Cloud

Airbyte Cloud runs and syncs your data using a specific set of IP addresses. Allow these IPs in your firewall to ensure Airbyte users can correctly use the platform.

Airbyte defaults to running syncs in the United States. To change this, or to check your data residency, see your [data residency](/platform/cloud/managing-airbyte-cloud/manage-data-residency) for each workspace.

<AirbyteCloudIps />

## Context layer

If your organization uses the [context layer](../context-layer/readme.md), agent access and search also use the following IP addresses. Allow them in addition to the Airbyte Cloud IP addresses.

| Geography     | Region    | IP address (CIDR) | IP addresses   |
| ------------- | --------- | ----------------- | -------------- |
| United States | us-west-2 | N/A               | 44.226.44.242  |
| United States | us-west-2 | N/A               | 35.163.106.179 |
| United States | us-west-2 | N/A               | 44.227.212.246 |
