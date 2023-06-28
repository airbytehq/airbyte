# Starburst Galaxy destination connector bootstrap

This destination syncs data to Amazon S3 catalog in [Starburst Galaxy](https://www.starburst.io/platform/starburst-galaxy/) by completing the following steps:

1. Persist source stream data to S3 staging storage in the Iceberg table format.
2. Create a destination Iceberg table in Amazon S3 catalog in Starburst Galaxy from the staged Iceberg table.

Learn more from [the Airbyte documentation](https://docs.airbyte.io/integrations/destinations/starburst-galaxy).
