---
products: all
---

# Faster sync speed

Airbyte is making major investments into the platform's sync speed. This page explains what you need to know about these speed improvements and how we're rolling them out.

## What is faster sync speed?

Faster sync speed is an initiative that drastically improves Airbyte's sync speeds. Initial benchmarking from MySQL to S3 has produced sync speeds up to 100 megabytes per second, depending on factors like compute infrastructure and data format. This is many times the old benchmark for this combination of connectors, but it might not be typical of all environments.

At this time, this capability is turned on for a small subset of connectors. At a point in the future, Airbyte expects to make this technology generally available, and to turn on support for a broad set of connectors. At that time, we'll communicate more about the expected benefits and speed benchmarks.

## How to use faster sync speed

The following Airbyte versions are eligible to use these speed enhancements.

- Self-Managed Community or Enterprise version 1.8 and later
- Cloud

To use faster sync speeds, a connection needs to use a source connector _and_ destination connector for which Airbyte has turned on faster syncs. You also need to upgrade to a version of those connectors that supports faster speed. You don't need to configure anything else.

## What connectors use improved speeds

Airbyte may enable additional connector combinations as the team works toward general availability. If you're using the latest connector versions, you might notice increases in sync speed for certain connections. This is Airbyte expanding the roll out.

Currently, these are the source and destination connectors that support faster sync speed.

### Sources

- MySQL

### Destinations

- S3
