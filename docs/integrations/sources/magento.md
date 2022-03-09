# Magento

[Magento](https://magento.com/products/magento-open-source) is an open source eCommerce Platform.

## Sync overview

There is a dedicated Magento2 source connector. The Magento2 source connector is based on the REST API. You just need an Access Token

### Features

| Feature | Supported? |
| :--- | :--- |
| Full Refresh Sync | Yes |
| Incremental Sync | Yes |
| SSL connection | Yes |
| Namespaces | Yes |

## Changelog

| Version | Date | Pull Request | Subject |
| :--- | :--- | :--- | :--- |
| 0.1.0 | 2021-07-26 | | Initial release supporting the Magento2 REST API |



If there is for some reason the REST API doesn't work, or you use Magento1, then you can consider the next possibility.
Magento runs on MySQL. You can use Airbyte to sync your Magento instance by connecting to the underlying database using the [MySQL connector](mysql.md).

{% hint style="info" %}
Reach out to your service representative or system admin to find the parameters required to connect to the underlying database
{% endhint %}

### Output schema

The output schema is described in the [Magento docs](https://docs.magento.com/mbi/data-analyst/importing-data/integrations/magento-data.html). See the [MySQL connector](mysql.md) for more info on general rules followed by the MySQL connector when moving data.

