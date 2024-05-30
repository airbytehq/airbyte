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

| Version | Date       | Pull Request | Subject                                              |
| :------ | :--------- | :----------- | :--------------------------------------------------- |
| 0.2.0   | 2023-11-10 |              | Update KYVE source to support to Mainnet and Testnet |
| 0.1.0   | 2023-05-25 |              | Initial release of KYVE source connector             |
