---
products: cloud
---

# IP allow list for Cloud

Airbyte Cloud runs and syncs your data using a specific set of IP addresses. Allow these IPs in your firewall to ensure Airbyte users can correctly use the platform.

Airbyte defaults to running syncs in the United States. To change this, or to check your data residency, see your [data residency](/platform/cloud/managing-airbyte-cloud/manage-data-residency) for each workspace.

## Google Cloud Platform

| Geography     | Region       | IP address (CIDR) | IP addresses   |
| ------------- |--------------|-------------------|----------------|
| United States | us-west-3    | N/A               | 34.106.109.131 |
| United States | us-west-3    | N/A               | 34.106.196.165 |
| United States | us-west-3    | N/A               | 34.106.60.246  |
| United States | us-west-3    | N/A               | 34.106.229.69  |
| United States | us-west-3    | N/A               | 34.106.127.139 |
| United States | us-west-3    | N/A               | 34.106.218.58  |
| United States | us-west-3    | N/A               | 34.106.115.240 |
| United States | us-west-3    | N/A               | 34.106.225.141 |
| United States | us-central-1 | 34.33.7.0/29      | 34.33.7.[0,8]  |

## AWS

| Geography | Region    | IP address (CIDR) | IP addresses   |
| --------- | --------- | ----------------- | -------------- |
| France    | eu-west-3 | N/A               | 13.37.4.46     |
| France    | eu-west-3 | N/A               | 13.37.142.60   |
| France    | eu-west-3 | N/A               | 35.181.124.238 |
