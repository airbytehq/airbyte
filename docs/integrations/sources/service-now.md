# Source ServiceNow

:::info
Airbyte Enterprise Connectors are a selection of premium connectors available exclusively for Airbyte Self-Managed Enterprise and Airbyte Teams customers. These connectors, built and maintained by the Airbyte team, provide enhanced capabilities and support for critical enterprise systems. To learn more about enterprise connectors, please [talk to our sales team](https://airbyte.com/company/talk-to-sales).
:::

Airbyte’s incubating ServiceNow enterprise source connector currently offers Full Refresh syncs for streams that are part of Software Asset Management and Configuration Management Database applications.

## Features

| Feature           | Supported?\(Yes/No\) | Notes |
| :---------------- | :------------------- | :---- |
| Full Refresh Sync | Yes                  |       |
| Incremental Sync  | No                   |       |

## Setup Guide

1. Enter your ServiceNow environment as the Base URL.
2. Enter the username and password for a ServiceNow user account that has access to all tables that you want to include in the connection.

![ServiceNow Connector setup with credentials](https://raw.githubusercontent.com/airbytehq/airbyte/refs/heads/master/docs/enterprise-setup/assets/enterprise-connectors/service-now-setup.png)

## Supported streams

### Configuration Management Database (CMDB)

- cmdb_ci_wap_network
- cmdb_ci_ip_router
- cmdb_ci_ip_switch
- cmdb_ci_lb_bigip
- cmdb_ci_ip_firewall
- cmdb_ci_printer
- cmdb_ci_scanner
- cmdb_ci_linux_server
- cmdb_ci_comm
- cmdb_ci_win_server
- cmdb_ci_ucs_chassis
- cmdb_ci_storage_switch
- cmdb_ci_pc_hardware
- cmdb_ci_esx_server
- cmdb_ci_aix_server
- cmdb_ci_solaris_server
- cmdb_ci_chassis_server
- cmdb_ci_server
- cmdb_ci_net_app_server

### Software Asset Management (SAM)

- cmdb_model_category
- sam_sw_product_lifecycle
- alm_license

