# WooCommerce

[WooCommerce](https://woocommerce.com/) is an open source eCommerce platform built on Wordpress.

## Sync overview

WooCommerce runs on a MySQL database. You can use Airbyte to sync your WooCommerce instance by connecting to the underlying MySQL database and leveraging the [MySQL](./mysql.md) connector.  

{% hint style="info" %}
Reach out to your service representative or system admin to find the parameters required to connect to the underlying database 
{% endhint %}


### Output schema
The output schema is the same as that of the [WooCommerce Database](https://github.com/woocommerce/woocommerce/wiki/Database-Description) described here. 
