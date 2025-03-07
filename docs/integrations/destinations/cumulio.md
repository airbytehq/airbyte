# Cumul.io

## General

The Airbyte Cumul.io destination connector allows you to stream data into Cumul.io from
[any Airbyte Source](https://airbyte.io/connectors?connector-type=Sources).

Cumul.io is an **[Embedded analytics SaaS solution](https://cumul.io/product/embedded-analytics)**
that enables other SaaS companies to grow with an **engaging customer analytics experience**,
seamlessly embedded in their product. Cumul.io's intuitive, low-code interface empowers business
users with insight-driven actions in record time **without straining engineering resources from the
core product**.

## Getting started

In order to use the Cumul.io destination, you'll first need to **create a
[Cumul.io account](https://app.cumul.io/signup)** (if you don’t already have one). After logging in
to Cumul.io, you can **generate an API key and token** in your
[Profile -> API Tokens](https://app.cumul.io/start/profile/integration). To set up the destination
connector in Airbyte, you'll need to provide the following Cumul.io properties:

- "**Cumul.io API Host URL**": the API host URL for the **Cumul.io environment** where your
  **Cumul.io account resides** (i.e. `https://api.cumul.io` for EU multi-tenant users,
  `https://api.us.cumul.io/` for US multi-tenant users, or a VPC-specific address). This property
  depends on the environment in which your Cumul.io account was created (e.g. if you have signed up
  via https://app.us.cumul.io/signup, the API host URL would be `https://api.us.cumul.io/`).
- "**Cumul.io API key**": a Cumul.io API key (see above how to generate an API key-token pair)
- "**Cumul.io API token**": the corresponding Cumul.io API token (see above how to generate an API
  key-token pair)

As soon as you've connected a source and the **first stream synchronization** has **succeeded**, the
desired **Dataset(s)** will be **available in Cumul.io to build dashboards on** (Cumul.io's
["Getting started" Academy course](https://academy.cumul.io/course/a0bf5530-edfb-441e-901b-e1fcb95dfac7)
might be interesting to get familiar with its platform). Depending on the **synchronization mode**
set up, the **next synchronizations** will either **replace/append data in/to these datasets**!

_If you have any questions or want to get started with Cumul.io, don't hesitate to reach out via
[our contact page](https://cumul.io/contact)._

## Connector overview

### Sync modes support

| [Sync modes](https://docs.airbyte.com/understanding-airbyte/connections/#sync-modes)                                     | Supported?\(Yes/No\) | Notes                                                 |
| :----------------------------------------------------------------------------------------------------------------------- | :------------------- | :---------------------------------------------------- |
| [Full Refresh - Append](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-append/)                 | Yes                  | /                                                     |
| [Full Refresh - Replace](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-overwrite/)             | Yes                  | /                                                     |
| [Incremental Sync - Append](https://docs.airbyte.com/understanding-airbyte/connections/incremental-append/)              | Yes                  | /                                                     |
| [Incremental - Append + Deduped ](https://docs.airbyte.com/understanding-airbyte/connections/incremental-append-deduped) | No                   | Cumul.io's data warehouse does not support dbt (yet). |

### Airbyte Features support

| Feature                                                                  | Supported?\(Yes/No\) | Notes                                                                                                                                                                                                                                                                                                                                                                                               |
| :----------------------------------------------------------------------- | :------------------- | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [Namespaces](https://docs.airbyte.com/understanding-airbyte/namespaces/) | Yes                  | (**_Highly recommended_**) A **concatenation of the namespace and stream name** will be used as a unique identifier for the related Cumul.io dataset (using [Tags](https://academy.cumul.io/article/mam7lkdt)) and ensures next synchronizations can target the same dataset. Use this property to **ensure identically named destination streams** from different connections **do not coincide**! |
| [Clear data](https://docs.airbyte.com/operator-guides/clear)             | Yes                  | **Existing data** in a dataset is **not deleted** upon resetting a stream in Airbyte, however the next synchronization batch will replace all existing data. This ensures that the dataset is never empty (e.g. upon disabling the synchronization), which would otherwise result in "No data" upon querying it.                                                                                    |

### Airbyte data types support

| [Airbyte data types](https://docs.airbyte.com/understanding-airbyte/supported-data-types#the-types) | Remarks                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
| :-------------------------------------------------------------------------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Array & Object                                                                                      | To support a limited amount of insights, this connector will **stringify data values with type `Array` or `Object`** ([recommended by Airbyte](https://docs.airbyte.com/understanding-airbyte/supported-data-types/#unsupported-types)) as Cumul.io does not support storing nor querying such data types. For analytical purposes, it's always recommended to **unpack these values in different rows or columns** (depending on the use-case) before pushing the data to Cumul.io!                                                              |
| Time with(out) timezone                                                                             | While these values **will be stored as-is** in Cumul.io, they should be interpreted as `hierarchy`\* (i.e. text/string, see [Cumul.io's data types Academy article](https://academy.cumul.io/article/p68253bn)). Alternatively, you could either **provide a (default) date and timezone** for these values, or **unpack them in different columns** (e.g. `hour`, `minute`, `second` columns), before pushing the data to Cumul.io.                                                                                                              |
| Timestamp without timezone                                                                          | Cumul.io **does not support storing dates without timestamps**, these timestamps will be **interpreted as UTC date values**.                                                                                                                                                                                                                                                                                                                                                                                                                      |
| Number & Integer data types with NaN, Infinity, -Infinity values                                    | While these values **will be stored as-is** in Cumul.io, they will not support numeric aggregations such as sum, avg, etc. (_using such aggregations on these values likely causes unexpected behavior_). Ideally, such values are **converted into meaningful values** (e.g. no value, 0, a specific value, etc.) before pushing the data to Cumul.io.                                                                                                                                                                                           |
| Boolean                                                                                             | Boolean values **will be stringified** ([recommended by Airbyte](https://docs.airbyte.com/understanding-airbyte/supported-data-types/#unsupported-types)) and result in a hierarchy column type (i.e. text/string, see [Cumul.io's data types Academy article](https://academy.cumul.io/article/p68253bn)). You could use Cumul.io's hierarchy translation (see [this Academy article](https://academy.cumul.io/article/dqgn0316)) to assign translations to `true` and `false` that are meaningful to the business user in the column's context. |
| All other data types                                                                                | Should be supported and correctly interpreted by Cumul.io's Data API service\*.                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |

\*_Note: It might be that Cumul.io's automatic typing could initially interpret this type of data
wrongly due to its format (see `Possible future improvements` below), you could then alter the
column type in the Cumul.io UI to try changing it manually._

### Output schema in Cumul.io

Each replicated stream from Airbyte will output data into a corresponding dataset in Cumul.io. Each
dataset will **initially** have an **`Airbyte - <namespace><stream_name>` English name** which can
be **further adapted in Cumul.io's UI**, or even
[via API](https://developer.cumul.io/#dashboard_update). If the request of pushing a batch of data
fails, the connector will gracefully retry pushing the batch up to three times, with a backoff
interval of 5 minutes, 10 minutes, and 20 minutes, respectively.

The connector will **associate one or more of the following tags to each dataset**:

- `[AIRBYTE - DO NOT DELETE] - <namespace><stream_name>`: this tag will be **used to retrieve the
  dataset ID and its current columns** from Cumul.io, and will be associated with the dataset after
  the first batch of data is written to a new dataset.
- `[AIRBYTE - DO NOT DELETE] - REPLACE DATA`: this tag will be **associated to a dataset** when it
  should be "resetted" (i.e. the **existing data should be replaced**, see `Feature` -> `Reset data`
  above). The first batch of data of the next synchronization will replace all existing data if this
  tag is present on a dataset.

As noted in the tag name, it is important to **never remove such tags from the dataset(s) nor
manually set them** on other datasets. Doing so might break existing or new synchronizations!

## Data recommendations

### Data structure

To ensure the most performant queries, we recommend to **denormalize your data as much as possible
beforehand** (this ensures that the least amount of joins are required to achieve your desired
insights). Denormalized datasets also ensure that they can be easily consumed by less technical
users, who often do not understand relations between tables! Instead of denormalizing your datasets
to specific insights, it is recommended to **set up one or more dimensional data models** that
support all kinds of slicing and dicing within a dashboard: this ensures a **flexible & scalable
setup** which is **easy-to-understand and performant-to-query**!

This Cumul.io blog post goes into more detail on why customer-facing analytics requires a simple
data model: https://blog.cumul.io/2022/12/07/why-a-dimensional-data-model-for-embedded-analytics/.

### Pushing data

Cumul.io uses an **OLAP database** to **ensure the most performant concurrent "Read" queries** on
large amounts of data. OLAP databases, such as Cumul.io's database, are however often less suitable
for a lot of "Write" queries with small amounts of data.

To ensure the best performance when writing data, we **recommend synchronizing larger amounts of
data less frequently** rather than _smaller amounts of data more frequently_!

## Possible future improvements

- In case of many concurrent synchronizations, the following issues might arise at one point (not
  evaluated yet):
  - The combination of all write buffers' data could cause memory overload, in that case it might be
    interesting to alter the flush rate by changing the `flush_interval` variable in
    `destination_cumulio/writer.py` (currently set to 10 000, which is the maximum amount of data
    points that can be sent via Cumul.io's Data API service in a single request, see note
    [here](https://developer.cumul.io/#data_create)). We do recommend keeping the `flush_interval`
    value **as high as possible** to ensure the least amount of total overhead on all batches
    pushed!
  - Having more than 200 concurrent Airbyte connections flushing the data simultaneously, and using
    the same Cumul.io API key and token for each connection, might run into
    [Cumul.io's API Rate limit](https://developer.cumul.io/#core_api_ratelimiting). As this will
    rarely occur due to Cumul.io's burstable rate limit, we recommend using separate API key and
    tokens for identical destination connectors in case you would expect such concurrency. Note that
    synchronizing multiple streams in a single connection will happen sequentially and thus not run
    into the rate limit.
- The current connector will not take into account the Airbyte source data types, instead Cumul.io's
  API will automatically detect column types based on a random data sample. If Cumul.io's detected
  data type is not as desired, it's possible to alter the column's type via Cumul.io's UI to
  manually change the column type (e.g. if a `VARCHAR` column would only contain numeric values, it
  could initially be interpreted as a `numeric` column in Cumul.io but can at any point be changed
  to `hierarchy` if more appropriate).
  - As a future improvement, it is possible to:
    1. Create a new dataset -
       [Create Dataset API Documentation](https://developer.cumul.io/#dataset_create)
    2. Create the appropriate tag (`[AIRBYTE - DO NOT DELETE] - <stream_name>`) and associate it
       with the newly created dataset (in `destination_cumulio/client.py`, a method
       `_validate_tag_dataset_id_association(stream_name, dataset_id)` is defined which could be
       used for this step)
    3. Create each column with the correct Cumul.io type -
       [Create Column API Documentation](https://developer.cumul.io/#column_create)
    4. Associate each column with the dataset -
       [Associate Dataset Column API Documentation](https://developer.cumul.io/#column_assoc_dataset)
    5. From there on out, you can replace/append data for this dataset based on the tag (already
       implemented).

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                              | Subject                                             |
|:--------| :--------- | :-------------------------------------------------------- | :-------------------------------------------------- |
| 0.1.33 | 2025-02-22 | [54208](https://github.com/airbytehq/airbyte/pull/54208) | Update dependencies |
| 0.1.32 | 2025-02-15 | [53866](https://github.com/airbytehq/airbyte/pull/53866) | Update dependencies |
| 0.1.31 | 2025-02-01 | [52937](https://github.com/airbytehq/airbyte/pull/52937) | Update dependencies |
| 0.1.30 | 2025-01-25 | [51767](https://github.com/airbytehq/airbyte/pull/51767) | Update dependencies |
| 0.1.29 | 2025-01-11 | [51261](https://github.com/airbytehq/airbyte/pull/51261) | Update dependencies |
| 0.1.28 | 2024-12-28 | [50504](https://github.com/airbytehq/airbyte/pull/50504) | Update dependencies |
| 0.1.27 | 2024-12-21 | [50167](https://github.com/airbytehq/airbyte/pull/50167) | Update dependencies |
| 0.1.26 | 2024-12-14 | [49302](https://github.com/airbytehq/airbyte/pull/49302) | Update dependencies |
| 0.1.25 | 2024-11-25 | [48679](https://github.com/airbytehq/airbyte/pull/48679) | Update dependencies |
| 0.1.24 | 2024-11-04 | [47029](https://github.com/airbytehq/airbyte/pull/47029) | Update dependencies |
| 0.1.23 | 2024-10-12 | [46816](https://github.com/airbytehq/airbyte/pull/46816) | Update dependencies |
| 0.1.22 | 2024-10-05 | [46445](https://github.com/airbytehq/airbyte/pull/46445) | Update dependencies |
| 0.1.21 | 2024-09-28 | [46201](https://github.com/airbytehq/airbyte/pull/46201) | Update dependencies |
| 0.1.20 | 2024-09-21 | [45831](https://github.com/airbytehq/airbyte/pull/45831) | Update dependencies |
| 0.1.19 | 2024-09-14 | [45580](https://github.com/airbytehq/airbyte/pull/45580) | Update dependencies |
| 0.1.18 | 2024-09-07 | [45291](https://github.com/airbytehq/airbyte/pull/45291) | Update dependencies |
| 0.1.17 | 2024-08-31 | [45033](https://github.com/airbytehq/airbyte/pull/45033) | Update dependencies |
| 0.1.16 | 2024-08-24 | [44656](https://github.com/airbytehq/airbyte/pull/44656) | Update dependencies |
| 0.1.15 | 2024-08-22 | [44530](https://github.com/airbytehq/airbyte/pull/44530) | Update test dependencies |
| 0.1.14 | 2024-08-17 | [44283](https://github.com/airbytehq/airbyte/pull/44283) | Update dependencies |
| 0.1.13 | 2024-08-10 | [43695](https://github.com/airbytehq/airbyte/pull/43695) | Update dependencies |
| 0.1.12 | 2024-08-03 | [43178](https://github.com/airbytehq/airbyte/pull/43178) | Update dependencies |
| 0.1.11 | 2024-07-27 | [42780](https://github.com/airbytehq/airbyte/pull/42780) | Update dependencies |
| 0.1.10 | 2024-07-20 | [42281](https://github.com/airbytehq/airbyte/pull/42281) | Update dependencies |
| 0.1.9 | 2024-07-13 | [41711](https://github.com/airbytehq/airbyte/pull/41711) | Update dependencies |
| 0.1.8 | 2024-07-10 | [41341](https://github.com/airbytehq/airbyte/pull/41341) | Update dependencies |
| 0.1.7 | 2024-07-09 | [41104](https://github.com/airbytehq/airbyte/pull/41104) | Update dependencies |
| 0.1.6 | 2024-07-06 | [40763](https://github.com/airbytehq/airbyte/pull/40763) | Update dependencies |
| 0.1.5 | 2024-06-26 | [40507](https://github.com/airbytehq/airbyte/pull/40507) | Update dependencies |
| 0.1.4 | 2024-06-21 | [39930](https://github.com/airbytehq/airbyte/pull/39930) | Update dependencies |
| 0.1.3 | 2024-06-06 | [39292](https://github.com/airbytehq/airbyte/pull/39292) | [autopull] Upgrade base image to v1.2.2 |
| 0.1.2 | 2024-05-20 | [38371](https://github.com/airbytehq/airbyte/pull/38371) | [autopull] base image + poetry + up_to_date |
| 0.1.1   | 2024-03-05 | [#35838](https://github.com/airbytehq/airbyte/pull/35838) | Un-archive connector                                |
| 0.1.0   | 2023-02-16 |                                                           | Initial release of Cumul.io's Destination connector |

</details>
