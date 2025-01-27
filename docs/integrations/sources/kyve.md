# KYVE

This page contains the setup guide and reference information for the **KYVE** source connector.

The KYVE Data Pipeline enables easy import of KYVE data into any data warehouse or destination
supported by [Airbyte](https://airbyte.com/). With the `ELT` format, data analysts and engineers can now confidently source KYVE data without worrying about its validity or reliability.

For information about how to setup an end to end pipeline with this connector, see [the documentation](https://docs.kyve.network/data_engineers/accessing_data/elt_pipeline/overview).

## Source configuration setup

1. In order to create an ELT pipeline with KYVE source you should specify the **`Pool-ID`** of [KYVE storage pool](https://app.kyve.network/#/pools) from which you want to retrieve data.

2. You can specify a specific **`Bundle-Start-ID`** in case you want to narrow the records that will be retrieved from the pool. You can find the valid bundles of in the KYVE app (e.g. [Cosmos Hub pool](https://app.kyve.network/#/pools/0/bundles)).

3. In order to extract the validated from KYVE, you can specify the endpoint which will be requested **`KYVE-API URL Base`**. By default, the official KYVE **`mainnet`** endpoint will be used, providing the data of [these pools](https://app.kyve.network/#/pools).

   **_Note:_**
   KYVE Network consists of three individual networks: _Korellia_ is the `devnet` used for development purposes, _Kaon_ is the `testnet` used for testing purposes, and **`mainnet`** is the official network. Although through Kaon and Korellia validated data can be used for development purposes, it is recommended to only trust the data validated on Mainnet.

## Multiple pools

You can fetch with one source configuration more than one pool simultaneously. You just need to specify the **`Pool-IDs`** and the **`Bundle-Start-ID`** for the KYVE storage pool you want to archive separated with comma.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request | Subject                                              |
| :------ | :--------- | :----------- | :--------------------------------------------------- |
| 0.2.27 | 2025-01-25 | [51779](https://github.com/airbytehq/airbyte/pull/51779) | Update dependencies |
| 0.2.26 | 2025-01-11 | [51140](https://github.com/airbytehq/airbyte/pull/51140) | Update dependencies |
| 0.2.25 | 2024-12-28 | [50668](https://github.com/airbytehq/airbyte/pull/50668) | Update dependencies |
| 0.2.24 | 2024-12-21 | [50149](https://github.com/airbytehq/airbyte/pull/50149) | Update dependencies |
| 0.2.23 | 2024-12-14 | [48985](https://github.com/airbytehq/airbyte/pull/48985) | Update dependencies |
| 0.2.22 | 2024-11-25 | [48651](https://github.com/airbytehq/airbyte/pull/48651) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.2.21 | 2024-11-04 | [48190](https://github.com/airbytehq/airbyte/pull/48190) | Update dependencies |
| 0.2.20 | 2024-10-28 | [47078](https://github.com/airbytehq/airbyte/pull/47078) | Update dependencies |
| 0.2.19 | 2024-10-12 | [46477](https://github.com/airbytehq/airbyte/pull/46477) | Update dependencies |
| 0.2.18 | 2024-09-28 | [45815](https://github.com/airbytehq/airbyte/pull/45815) | Update dependencies |
| 0.2.17 | 2024-09-14 | [45493](https://github.com/airbytehq/airbyte/pull/45493) | Update dependencies |
| 0.2.16 | 2024-09-07 | [45219](https://github.com/airbytehq/airbyte/pull/45219) | Update dependencies |
| 0.2.15 | 2024-08-31 | [44955](https://github.com/airbytehq/airbyte/pull/44955) | Update dependencies |
| 0.2.14 | 2024-08-24 | [44687](https://github.com/airbytehq/airbyte/pull/44687) | Update dependencies |
| 0.2.13 | 2024-08-17 | [44218](https://github.com/airbytehq/airbyte/pull/44218) | Update dependencies |
| 0.2.12 | 2024-08-10 | [43671](https://github.com/airbytehq/airbyte/pull/43671) | Update dependencies |
| 0.2.11 | 2024-08-03 | [43059](https://github.com/airbytehq/airbyte/pull/43059) | Update dependencies |
| 0.2.10 | 2024-07-27 | [42736](https://github.com/airbytehq/airbyte/pull/42736) | Update dependencies |
| 0.2.9 | 2024-07-20 | [42279](https://github.com/airbytehq/airbyte/pull/42279) | Update dependencies |
| 0.2.8 | 2024-07-13 | [41749](https://github.com/airbytehq/airbyte/pull/41749) | Update dependencies |
| 0.2.7 | 2024-07-10 | [41422](https://github.com/airbytehq/airbyte/pull/41422) | Update dependencies |
| 0.2.6 | 2024-07-09 | [41239](https://github.com/airbytehq/airbyte/pull/41239) | Update dependencies |
| 0.2.5 | 2024-07-06 | [40859](https://github.com/airbytehq/airbyte/pull/40859) | Update dependencies |
| 0.2.4 | 2024-06-26 | [40268](https://github.com/airbytehq/airbyte/pull/40268) | Update dependencies |
| 0.2.3 | 2024-06-24 | [40049](https://github.com/airbytehq/airbyte/pull/40049) | Update dependencies |
| 0.2.2 | 2024-06-04 | [39004](https://github.com/airbytehq/airbyte/pull/39004) | [autopull] Upgrade base image to v1.2.1 |
| 0.2.1 | 2024-05-21 | [38514](https://github.com/airbytehq/airbyte/pull/38514) | [autopull] base image + poetry + up_to_date |
| 0.2.0   | 2023-11-10 |              | Update KYVE source to support to Mainnet and Testnet |
| 0.1.0   | 2023-05-25 |              | Initial release of KYVE source connector             |

</details>
