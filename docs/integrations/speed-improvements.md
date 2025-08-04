---
products: all
---

# Faster sync speed

Airbyte is making major investments into the platform's sync speed. This page explains more about how Airbyte is improving sync speeds and how it's rolling out those changes to you.

## What is faster sync speed?

Faster sync speed is an initiative that drastically improves Airbyte's sync speeds. Initial benchmarking from MySQL to S3 has produced sync speeds up to 100 megabytes per second, depending on factors like compute infrastructure and data format. This is many times the old benchmark for this combination of connectors, but it might not be typical of all environments.

At this time, this capability is turned on for a small subset of connectors. At a point in the future, Airbyte expects to make this technology generally available, and to turn on support for a broad set of connectors. At that time, we'll communicate more about the expected benefits and speed benchmarks.

## How to be eligible for improved speed

The following platform versions are eligible to use these speed enhancements.

- Self-Managed Community or Enterprise version 1.8 and later
- Cloud

Improved speed isn't widely usable with most connectors yet. To benefit from faster sync speeds, a connection needs to use a source connector _and_ destination connector for which Airbyte has turned on faster syncs. You also need to upgrade to the version of that connector that supports faster speed.

Airbyte may enable additional connector combinations as the team works toward general availability. If you're using the latest connector versions, you might notice increases in sync speed for certain connections. This is Airbyte expanding the roll out.

## What connectors use improved speeds

import EnhancedSpeedConnectors from '@site/src/components/EnhancedSpeedConnectors';

### Sources

<EnhancedSpeedConnectors type="source"/>

### Destinations  

<EnhancedSpeedConnectors type="destination"/>
