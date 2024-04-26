# Slack Migration Guide

## Upgrading to 1.0.0

We're continuously striving to enhance the quality and reliability of our connectors at Airbyte. 
As part of our commitment to delivering exceptional service, we are transitioning source Slack from the
Python Connector Development Kit (CDK) to our innovative low-code framework. 
This is part of a strategic move to streamline many processes across connectors, bolstering maintainability and 
freeing us to focus more of our efforts on improving the performance and features of our evolving platform and growing catalog.
However, due to differences between the Python and low-code CDKs, this migration constitutes a breaking change. 

We’ve evolved and standardized how state is managed for incremental streams that are nested within a parent stream. 
This change impacts how individual states are tracked and stored for each partition, using a more structured approach
to ensure the most granular and flexible state management.
This change will affect the `Channel Messages` stream.

## Migration Steps
* A `reset` for `Channel Messages` stream is required after upgrading to this version.
