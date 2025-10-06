---
products: all
---

# Faster sync speed

Airbyte has made major investments into the platform's sync speed. This page explains what you need to know about these speed improvements and how you can take advantage of them.

## What's faster sync speed?

Faster sync speed is an initiative that drastically improves Airbyte's sync speeds. Airbyte has turned on this capability for a subset of connectors. Airbyte continues to make faster speed available to a growing number of connectors.

### How much faster is Airbyte?

As a general rule, sync speeds for supported connectors are between 4 and 10 times faster than they were historically, and maintain these levels even with more economical resource allocation.

The exact performance gains you can expect depend on the connectors in use and, if you're self-managing Airbyte, your own infrastructure. Specifically, the CPU type for Kubernetes nodes offers an opportunity for significant performance gains and resource savings.

Airbyte ran benchmarks on Google Compute Engine. Below are the results after syncing from MySQL to S3 using a 170.68 GB dataset. Airbyte's general finding is that CPU performance is now directly correlated with speed and efficiency. Testers achieved the best outcomes with high-performance CPUs (C4). However, even medium-performance CPUs like N2D delivered swift performance. In all cases, test connections were more economical and used reduced resource requirements.

#### Benchmarks with nodes on C4

| Category              | Before             | After                         |
| --------------------- | ------------------ | ----------------------------- |
| Source container      | 4 CPU / 4 GB RAM   | 4 CPU / 4 GB RAM              |
| Destination container | 4 CPU / 4 GB RAM   | 4 CPU / 4 GB RAM              |
| Orchestrator          | 4 CPU / 4 GB RAM   | 1 CPU / 1 GB RAM              |
| Total resources       | 12 CPU / 12 GB RAM | 9 CPU / 9 GB RAM (~25% fewer) |
| Data volume           | 170.68 GB          | 170.68 GB                     |
| Time taken            | 1 h 35 m           | 22m (~4 times faster)         |

#### Benchmarks with nodes on N2D

| Category              | Before           | After                         |
| --------------------- | ---------------- | ----------------------------- |
| Source container      | 2 CPU / 2 GB RAM | 2 CPU / 2 GB RAM              |
| Destination container | 2 CPU / 2 GB RAM | 2 CPU / 2 GB RAM              |
| Orchestrator          | 2 CPU / 2 GB RAM | 1 CPU / 1 GB RAM              |
| Total resources       | 6 CPU / 6 GB RAM | 5 CPU / 5 GB RAM (~17% fewer) |
| Data volume           | 170.68 GB        | 170.68 GB                     |
| Time taken            | 5 h 21 m         | 1 h (~5 times faster)         |

## How to use faster sync speed

The following Airbyte versions are eligible to use these speed enhancements.

- Self-Managed versions 1.8 and later
- Cloud

To use faster sync speed:

- A connection needs to use a source connector _and_ destination connector for which Airbyte has turned on faster syncs.
- You need to upgrade to a version of those connectors that supports faster speed.
- If you use a self-managed plan, you need to upgrade to version 1.8 or later. If you use a Cloud plan, you don't need to do anything.

## What connectors use faster speed

Airbyte may enable additional connector combinations as the team works toward general availability. If you're using the latest connector versions, you might notice increases in sync speed for certain connections. This is Airbyte expanding the roll out.

Currently, these are the source and destination connectors that support faster sync speed.

### Sources

- [MySQL](sources/mysql)

### Destinations

- [S3](destinations/s3)
- [Azure Blob Storage](destinations/azure-blob-storage)
- [BigQuery](destinations/bigquery)
- [ClickHouse](destinations/clickhouse)
