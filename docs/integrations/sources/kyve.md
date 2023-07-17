# Kyve Source

This page contains the setup guide and reference information for the **KYVE** source connector.

The KYVE Data Pipeline enables easy import of KYVE data into any data warehouse or destination
supported by [Airbyte](https://airbyte.com/). With the `ELT` format, data analysts and engineers can now confidently source KYVE data without worrying about its validity or reliability.

For information about how to setup an end to end pipeline with this connector, see [the documentation](https://docs.kyve.network/data_engineers/accessing_data/elt_pipeline/overview).

## Source configuration setup

1. In order to  create an ELT pipeline with KYVE source you should specify the **`Pool-ID`** of [Kyve storage pool](https://app.kyve.network/#/pools) from which you want to retrieve data.

2. You can specify a specific **`Bundle-Start-ID`** in case you want to narrow the records that will be retrieved from the pool. You can find the valid bundles of in the KYVE app (e.g. [Moonbeam pool bundles](https://app.kyve.network/#/pools/0/bundles)).

## Multiple pools
You can fetch with one source configuration more than one pool simultaneously. You just need to specify the **`Pool-IDs`** and the **`Bundle-Start-ID`** for the KYVE storage pool you want to archive separated with comma.

## Changelog

| Version | Date | Pull Request | Subject          |
|:--------| :--- | :----------- | :--------------- |
| 0.1.0   | 25-05-29  | [26299](https://github.com/airbytehq/airbyte/pull/26299) | Initial release of KYVE source connector|
