# Luzmo

## General

The Airbyte Luzmo destination connector allows you to stream data into Luzmo from [any Airbyte Source](https://airbyte.io/connectors?connector-type=Sources).

Luzmo is an **[Embedded analytics SaaS solution](https://luzmo.com/product/embedded-analytics)** that enables other SaaS companies to grow with an **engaging customer analytics experience**, seamlessly embedded in their product. Luzmo's intuitive, low-code interface empowers business users with insight-driven actions in record time **without straining engineering resources from the core product**.

## Getting started

In order to use the Luzmo destination, you'll first need to **create a [Luzmo account](https://app.luzmo.com/signup)** (if you don’t already have one).
After logging in to Luzmo, you can **generate an API key and token** in your [Profile -> API Tokens](https://app.luzmo.com/start/profile/integration).
To set up the destination connector in Airbyte, you'll need to provide the following Luzmo properties:

- "**Luzmo API Host URL**": the API host URL for the **Luzmo environment** where your **Luzmo account resides** (i.e. `https://api.luzmo.com` for EU multi-tenant users, `https://api.us.luzmo.com/` for US multi-tenant users, or a VPC-specific address). This property depends on the environment in which your Luzmo account was created (e.g. if you have signed up via https://app.us.luzmo.com/signup, the API host URL would be `https://api.us.luzmo.com/`).
- "**Luzmo API key**": a Luzmo API key (see above how to generate an API key-token pair)
- "**Luzmo API token**": the corresponding Luzmo API token (see above how to generate an API key-token pair)

As soon as you've connected a source and the **first stream synchronization** has **succeeded**, the desired **Dataset(s)** will be **available in Luzmo to build dashboards on** (Luzmo's ["Getting started" Academy course](https://academy.luzmo.com/course/a0bf5530-edfb-441e-901b-e1fcb95dfac7) might be interesting to get familiar with its platform).
Depending on the **synchronization mode** set up, the **next synchronizations** will either **replace/append data in/to these datasets**!

_If you have any questions or want to get started with Luzmo, don't hesitate to reach out via [our contact page](https://www.luzmo.com/book-a-demo)._

## Connector overview

### Sync modes support

| [Sync modes](https://docs.airbyte.com/understanding-airbyte/connections/#sync-modes)                                     | Supported?\(Yes/No\) | Notes                                                 |
| :----------------------------------------------------------------------------------------------------------------------- | :------------------- | :---------------------------------------------------- |
| [Full Refresh - Append](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-append/)                 | Yes                  | /                                                     |
| [Full Refresh - Replace](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-overwrite/)             | Yes                  | /                                                     |
| [Incremental Sync - Append](https://docs.airbyte.com/understanding-airbyte/connections/incremental-append/)              | Yes                  | /                                                     |
| [Incremental - Append + Deduped ](https://docs.airbyte.com/understanding-airbyte/connections/incremental-append-deduped) | No                   | Luzmo's data warehouse does not support dbt (yet). |

### Airbyte Features support

| Feature                                                                  | Supported?\(Yes/No\) | Notes                                                                                                                                                                                                                                                                                                                                                                                               |
| :----------------------------------------------------------------------- | :------------------- | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [Namespaces](https://docs.airbyte.com/understanding-airbyte/namespaces/) | Yes                  | (**_Highly recommended_**) A **concatenation of the namespace and stream name** will be used as a unique identifier for the related Luzmo dataset (using [Tags](https://academy.luzmo.com/article/mam7lkdt)) and ensures next synchronizations can target the same dataset. Use this property to **ensure identically named destination streams** from different connections **do not coincide**! |
| [Reset data](https://docs.airbyte.com/operator-guides/reset)             | Yes                  | **Existing data** in a dataset is **not deleted** upon resetting a stream in Airbyte, however the next synchronization batch will replace all existing data. This ensures that the dataset is never empty (e.g. upon disabling the synchronization), which would otherwise result in "No data" upon querying it.                                                                                    |

### Airbyte data types support

| [Airbyte data types](https://docs.airbyte.com/understanding-airbyte/supported-data-types#the-types) | Remarks                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
| :-------------------------------------------------------------------------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Array & Object                                                                                      | To support a limited amount of insights, this connector will **stringify data values with type `Array` or `Object`** ([recommended by Airbyte](https://docs.airbyte.com/understanding-airbyte/supported-data-types/#unsupported-types)) as Luzmo does not support storing nor querying such data types. For analytical purposes, it's always recommended to **unpack these values in different rows or columns** (depending on the use-case) before pushing the data to Luzmo!                                                              |
| Time with(out) timezone                                                                             | While these values **will be stored as-is** in Luzmo, they should be interpreted as `hierarchy`\* (i.e. text/string, see [Luzmo's data types Academy article](https://academy.luzmo.com/article/p68253bn)). Alternatively, you could either **provide a (default) date and timezone** for these values, or **unpack them in different columns** (e.g. `hour`, `minute`, `second` columns), before pushing the data to Luzmo.                                                                                                              |
| Timestamp without timezone                                                                          | Luzmo **does not support storing dates without timestamps**, these timestamps will be **interpreted as UTC date values**.                                                                                                                                                                                                                                                                                                                                                                                                                      |
| Number & Integer data types with NaN, Infinity, -Infinity values                                    | While these values **will be stored as-is** in Luzmo, they will not support numeric aggregations such as sum, avg, etc. (_using such aggregations on these values likely causes unexpected behavior_). Ideally, such values are **converted into meaningful values** (e.g. no value, 0, a specific value, etc.) before pushing the data to Luzmo.                                                                                                                                                                                           |
| Boolean                                                                                             | Boolean values **will be stringified** ([recommended by Airbyte](https://docs.airbyte.com/understanding-airbyte/supported-data-types/#unsupported-types)) and result in a hierarchy column type (i.e. text/string, see [Luzmo's data types Academy article](https://academy.luzmo.com/article/p68253bn)). You could use Luzmo's hierarchy translation (see [this Academy article](https://academy.luzmo.com/article/dqgn0316)) to assign translations to `true` and `false` that are meaningful to the business user in the column's context. |
| All other data types                                                                                | Should be supported and correctly interpreted by Luzmo's Data API service\*.                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |

\*_Note: It might be that Luzmo's automatic typing could initially interpret this type of data wrongly due to its format (see `Possible future improvements` below), you could then alter the column type in the Luzmo UI to try changing it manually._

### Output schema in Luzmo

Each replicated stream from Airbyte will output data into a corresponding dataset in Luzmo. Each dataset will **initially** have an **`Airbyte - <namespace><stream_name>` English name** which can be **further adapted in Luzmo's UI**, or even [via API](https://developer.luzmo.com/#dashboard_update). If the request of pushing a batch of data fails, the connector will gracefully retry pushing the batch up to three times, with a backoff interval of 5 minutes, 10 minutes, and 20 minutes, respectively.

The connector will **associate one or more of the following tags to each dataset**:

- `[AIRBYTE - DO NOT DELETE] - <namespace><stream_name>`: this tag will be **used to retrieve the dataset ID and its current columns** from Luzmo, and will be associated with the dataset after the first batch of data is written to a new dataset.
- `[AIRBYTE - DO NOT DELETE] - REPLACE DATA`: this tag will be **associated to a dataset** when it should be "resetted" (i.e. the **existing data should be replaced**, see `Feature` -> `Reset data` above). The first batch of data of the next synchronization will replace all existing data if this tag is present on a dataset.

As noted in the tag name, it is important to **never remove such tags from the dataset(s) nor manually set them** on other datasets. Doing so might break existing or new synchronizations!

## Data recommendations

### Data structure

To ensure the most performant queries, we recommend to **denormalize your data as much as possible beforehand** (this ensures that the least amount of joins are required to achieve your desired insights). Denormalized datasets also ensure that they can be easily consumed by less technical users, who often do not understand relations between tables! Instead of denormalizing your datasets to specific insights, it is recommended to **set up one or more dimensional data models** that support all kinds of slicing and dicing within a dashboard: this ensures a **flexible & scalable setup** which is **easy-to-understand and performant-to-query**!

This Luzmo blog post goes into more detail on why customer-facing analytics requires a simple data model: https://www.luzmo.com/blog/dimensional-data-model-for-embedded-analytics.

### Pushing data

Luzmo uses an **OLAP database** to **ensure the most performant concurrent "Read" queries** on large amounts of data. OLAP databases, such as Luzmo's database, are however often less suitable for a lot of "Write" queries with small amounts of data.

To ensure the best performance when writing data, we **recommend synchronizing larger amounts of data less frequently** rather than _smaller amounts of data more frequently_!

## Possible future improvements

- In case of many concurrent synchronizations, the following issues might arise at one point (not evaluated yet):
  - The combination of all write buffers' data could cause memory overload, in that case it might be interesting to alter the flush rate by changing the `flush_interval` variable in `destination_luzmo/writer.py` (currently set to 10 000, which is the maximum amount of data points that can be sent via Luzmo's Data API service in a single request, see note [here](https://developer.luzmo.com/#data_create)). We do recommend keeping the `flush_interval` value **as high as possible** to ensure the least amount of total overhead on all batches pushed!
  - Having more than 200 concurrent Airbyte connections flushing the data simultaneously, and using the same Luzmo API key and token for each connection, might run into [Luzmo's API Rate limit](https://developer.luzmo.com/#core_api_ratelimiting). As this will rarely occur due to Luzmo's burstable rate limit, we recommend using separate API key and tokens for identical destination connectors in case you would expect such concurrency. Note that synchronizing multiple streams in a single connection will happen sequentially and thus not run into the rate limit.
- The current connector will not take into account the Airbyte source data types, instead Luzmo's API will automatically detect column types based on a random data sample. If Luzmo's detected data type is not as desired, it's possible to alter the column's type via Luzmo's UI to manually change the column type (e.g. if a `VARCHAR` column would only contain numeric values, it could initially be interpreted as a `numeric` column in Luzmo but can at any point be changed to `hierarchy` if more appropriate).
  - As a future improvement, it is possible to:
    1. Create a new dataset - [Create Dataset API Documentation](https://developer.luzmo.com/#dataset_create)
    2. Create the appropriate tag (`[AIRBYTE - DO NOT DELETE] - <stream_name>`) and associate it with the newly created dataset (in `destination_luzmo/client.py`, a method `_validate_tag_dataset_id_association(stream_name, dataset_id)` is defined which could be used for this step)
    3. Create each column with the correct Luzmo type - [Create Column API Documentation](https://developer.luzmo.com/#column_create)
    4. Associate each column with the dataset - [Associate Dataset Column API Documentation](https://developer.luzmo.com/#column_assoc_dataset)
    5. From there on out, you can replace/append data for this dataset based on the tag (already implemented).

## CHANGELOG

| Version | Date       | Pull Request | Subject                                             |
| :------ | :--------- | :----------- | :-------------------------------------------------- |
| 0.1.0   | 2023-02-16 |              | Initial release of Cumul.io's Destination connector |
| 0.2.0   | 2023-10-02 |              | Rebranding to Luzmo's Destination connector         |
