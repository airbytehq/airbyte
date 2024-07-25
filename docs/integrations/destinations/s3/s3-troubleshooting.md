# Troubleshooting S3 Destinations

## Connector Limitations

### Vendor-Specific Connector Limitations

:::warning

Not all implementations or deployments an "S3-compatible destinations" will be the same. This section lists specific limitations and known issues with the connector based on _how_ or
_where_ it is deployed.

:::

#### Linode Object Storage

Liniode Object Storage does not properly return etags after setting them, which Airbyte relies on to verify the integrity of the data. This makes this destination currently incompatible with Airbyte.
