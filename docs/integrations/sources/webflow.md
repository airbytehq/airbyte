---
description: 'This connector extracts "collections" from Webflow'
---

# Sources

Webflow is used for publishing Airbyte's blogs, and provides several APIs. The APIs that are used by this connector to extract information from Webflow are described in [Webflow Developers documentation](https://developers.webflow.com/). 

 Webflow uses [Collections](https://developers.webflow.com/#collections) to store different kinds of information. A collection can be "Blog Posts", or "Blog Authors", etc. Collection names are not pre-defined, the number of collections is not known in advance, and the schema for each collection may be different. Therefore this connector dynamically figures our which collections are available and downloads the schema for each collection from Webflow. Each collection is mapped to an [Airbyte Streams](https://docs.airbyte.com/connector-development/cdk-python/full-refresh-stream/). 