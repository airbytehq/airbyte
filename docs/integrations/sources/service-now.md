# Source ServiceNow

Airbyte’s incubating ServiceNow Enterprise source connector offers both Full Refresh and Incremental syncs for streams that are part of Software Asset Management (SAM), Configuration Management Database (CMDB), and IT Service Management (ITSM) applications.

## Setup Guide

1. Enter your ServiceNow environment as the Base URL.
2. Enter the username and password for a ServiceNow user account that has access to all tables that you want to include in the connection.

![ServiceNow Connector setup with credentials](https://raw.githubusercontent.com/airbytehq/airbyte/refs/heads/master/docs/enterprise-setup/assets/enterprise-connectors/service-now-setup.png)

## Supported streams

### Configuration Management Database (CMDB)

- cmdb_ci_aix_server
- cmdb_ci_chassis_server
- cmdb_ci_comm
- cmdb_ci_esx_server
- cmdb_ci_ip_firewall
- cmdb_ci_ip_router
- cmdb_ci_ip_switch
- cmdb_ci_lb_bigip
- cmdb_ci_linux_server
- cmdb_ci_net_app_server
- cmdb_ci_pc_hardware
- cmdb_ci_printer
- cmdb_ci_scanner
- cmdb_ci_server
- cmdb_ci_solaris_server
- cmdb_ci_storage_switch
- cmdb_ci_ucs_chassis
- cmdb_ci_wap_network
- cmdb_ci_win_server

### Software Asset Management (SAM)

- alm_license
- cmdb_model_category
- sam_sw_product_lifecycle

### IT Service Management (ITSM)

- acr_case
- approvals
- cancellations
- change_request
- create_customer_care_case
- credit_request
- customer_service_task
- general_procurement_question
- incident
- incident_to_ptask
- non_standard_deals
- problem
- problem_task
- purchase_request
- refund_request
- vendor_update

## Supported sync modes

The NetSuite source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

- Full Refresh
- Incremental

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Subject                                                   |
|:--------|:-----------|:----------------------------------------------------------|
|  0.2.0  | 2022-09-11 | Adds incremental support and new ITSM streams             |
|  0.1.1  | 2022-02-25 | Fix metadata                                              |
|  0.1.0  | 2022-02-18 | Initial Alpha release                                     |

</details>
