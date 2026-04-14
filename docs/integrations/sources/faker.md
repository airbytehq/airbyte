# Sample Data (Faker)

The Sample Data source generates realistic fake data using the Python [`mimesis`](https://mimesis.name/en/master/) library. It produces an e-commerce-like dataset useful for testing, demos, and development.

## Prerequisites

None. This connector generates data locally and does not connect to an external API.

## Supported streams

This source has three streams: `users`, `products`, and `purchases`. All streams support full refresh and incremental sync, with `id` as the primary key and `updated_at` as the cursor field.

### Users

Each user record contains identity and demographic fields: `id`, `created_at`, `updated_at`, `name`, `title`, `age`, `email`, `telephone`, `gender`, `language`, `academic_degree`, `nationality`, `occupation`, `height`, `blood_type`, `weight`, and an embedded `address` object with `street_number`, `street_name`, `city`, `state`, `province`, `postal_code`, and `country_code`. The number of user records is controlled by the `count` configuration option.

### Products

Product records represent vehicles with fields: `id`, `make`, `model`, `year`, `price`, `created_at`, and `updated_at`. The products stream draws from a fixed catalog of 100 products. The `count` option limits how many of those 100 products are emitted; setting `count` higher than 100 still produces at most 100 products.

### Purchases

Each purchase record includes: `id`, `user_id`, `product_id`, `created_at`, `updated_at`, `added_to_cart_at`, `purchased_at`, and `returned_at`. Items added to a cart have a 70% chance of being purchased, and purchased items have a 15% chance of being returned. The `purchased_at` and `returned_at` fields are nullable. The connector generates roughly one purchase per user, so the total number of purchases scales with `count`.

## Features

| Feature           | Supported? |
| :---------------- | :--------- |
| Full Refresh Sync | Yes        |
| Incremental Sync  | Yes        |
| Namespaces        | No         |

## Configuration

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| **Count** | integer | 1000 | The total number of user records to generate. The purchases stream scales proportionally. Does not affect the products stream beyond its 100-product catalog. |
| **Seed** | integer | -1 | Controls random data generation. Set a specific value to produce the same records on each sync. Leave at `-1` for random data. |
| **Always Updated** | boolean | true | When `true`, every sync emits all records with fresh `updated_at` timestamps. When `false`, the connector stops emitting records after the initial sync produces `count` records. |
| **Records Per Stream Slice** | integer | 1000 | The number of records per stream slice before a state checkpoint is emitted. |
| **Parallelism** | integer | 4 | The number of parallel workers for data generation. Set this to the number of CPUs allocated to the connector. |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version     | Date       | Pull Request                                                                                                          | Subject                                                                                                         |
|:------------|:-----------| :-------------------------------------------------------------------------------------------------------------------- |:----------------------------------------------------------------------------------------------------------------|
| 7.1.0 | 2026-03-31 | [75941](https://github.com/airbytehq/airbyte/pull/75941) | Promoted release candidate to GA |
| 7.1.0-rc.2 | 2026-03-31 | [75926](https://github.com/airbytehq/airbyte/pull/75926) | Bump source-faker to RC2 for progressive rollout e2e test |
| 7.1.0-rc.1 | 2026-03-31 | [75908](https://github.com/airbytehq/airbyte/pull/75908) | test: progressive rollout e2e test on source-faker |
| 7.0.4 | 2026-03-31 | [75657](https://github.com/airbytehq/airbyte/pull/75657) | Patch version bump (test publish) |
| 7.0.3 | 2026-03-20 | [75256](https://github.com/airbytehq/airbyte/pull/75256) | Re-release to verify yank/un-yank behavior in ops CLI registry pipeline |
| 7.0.2 | 2026-03-19 | [75232](https://github.com/airbytehq/airbyte/pull/75232) | Patch version bump (ops CLI registry post-launch test) |
| 7.0.1 | 2026-03-13 | [74818](https://github.com/airbytehq/airbyte/pull/74818) | Patch version bump (publish test) |
| 7.0.0 | 2026-03-05 | [74318](https://github.com/airbytehq/airbyte/pull/74318) | Test breaking change to validate breaking change infrastructure |
| 6.2.38 | 2025-11-12 | [69289](https://github.com/airbytehq/airbyte/pull/69289) | Add externalDocumentationUrls field to metadata |
| 6.2.37 | 2025-10-21 | [68572](https://github.com/airbytehq/airbyte/pull/68572) | Update dependencies |
| 6.2.36 | 2025-10-14 | [67806](https://github.com/airbytehq/airbyte/pull/67806) | Update dependencies |
| 6.2.35 | 2025-10-07 | [67290](https://github.com/airbytehq/airbyte/pull/67290) | Update dependencies |
| 6.2.34 | 2025-09-30 | [65779](https://github.com/airbytehq/airbyte/pull/65779) | Update dependencies |
| 6.2.33 | 2025-09-03 | [65914](https://github.com/airbytehq/airbyte/pull/65914) | Upgrade CDK to 6.28.0 and remove pendulum dependency |
| 6.2.32 | 2025-08-23 | [65273](https://github.com/airbytehq/airbyte/pull/65273) | Update dependencies |
| 6.2.31 | 2025-08-16 | [65006](https://github.com/airbytehq/airbyte/pull/65006) | Update dependencies |
| 6.2.30 | 2025-08-09 | [64799](https://github.com/airbytehq/airbyte/pull/64799) | Update dependencies |
| 6.2.29 | 2025-07-26 | [63953](https://github.com/airbytehq/airbyte/pull/63953) | Update dependencies |
| 6.2.28 | 2025-07-19 | [63534](https://github.com/airbytehq/airbyte/pull/63534) | Update dependencies |
| 6.2.27 | 2025-07-17 | [63354](https://github.com/airbytehq/airbyte/pull/63354) | Updated icon |
| 6.2.26 | 2025-07-16 | [63342](https://github.com/airbytehq/airbyte/pull/63342) | Rendered name changed to `Sample Data` |
| 6.2.26-rc.1 | 2025-06-16 | [61645](https://github.com/airbytehq/airbyte/pull/61645) | Update for testing |
| 6.2.25-rc.1 | 2025-04-07 | [57500](https://github.com/airbytehq/airbyte/pull/57500) | Update for testing |
| 6.2.24 | 2025-04-05 | [57263](https://github.com/airbytehq/airbyte/pull/57263) | Update dependencies |
| 6.2.23 | 2025-03-29 | [56502](https://github.com/airbytehq/airbyte/pull/56502) | Update dependencies |
| 6.2.22 | 2025-03-22 | [46821](https://github.com/airbytehq/airbyte/pull/46821) | Update dependencies |
| 6.2.21 | 2025-03-11 | [55705](https://github.com/airbytehq/airbyte/pull/55705) | Promoting release candidate 6.2.21-rc.1 to a main version. |
| 6.2.21-rc.1 | 2024-11-13 | [48013](https://github.com/airbytehq/airbyte/pull/48013) | Update for testing. |
| 6.2.20 | 2024-10-30 | [48013](https://github.com/airbytehq/airbyte/pull/48013) | Promoting release candidate 6.2.20-rc.1 to a main version. |
| 6.2.20-rc.1 | 2024-10-21 | [46678](https://github.com/airbytehq/airbyte/pull/46678) | Testing release candidate with RC suffix versioning. |
| 6.2.19-rc.1 | 2024-10-21 | [47221](https://github.com/airbytehq/airbyte/pull/47221) | Testing release candidate with RC suffix versioning. |
| 6.2.18-rc.1 | 2024-10-09 | [46678](https://github.com/airbytehq/airbyte/pull/46678) | Testing release candidate with RC suffix versioning. |
| 6.2.17 | 2024-10-05 | [46398](https://github.com/airbytehq/airbyte/pull/46398) | Update dependencies |
| 6.2.16 | 2024-09-28 | [46207](https://github.com/airbytehq/airbyte/pull/46207) | Update dependencies |
| 6.2.15 | 2024-09-21 | [45740](https://github.com/airbytehq/airbyte/pull/45740) | Update dependencies |
| 6.2.14 | 2024-09-14 | [45567](https://github.com/airbytehq/airbyte/pull/45567) | Update dependencies |
| 6.2.13 | 2024-09-07 | [45327](https://github.com/airbytehq/airbyte/pull/45327) | Update dependencies |
| 6.2.12 | 2024-09-04 | [45126](https://github.com/airbytehq/airbyte/pull/45126) | Test a release candidate release |
| 6.2.11 | 2024-08-31 | [45025](https://github.com/airbytehq/airbyte/pull/45025) | Update dependencies |
| 6.2.10 | 2024-08-24 | [44659](https://github.com/airbytehq/airbyte/pull/44659) | Update dependencies |
| 6.2.9 | 2024-08-17 | [44221](https://github.com/airbytehq/airbyte/pull/44221) | Update dependencies |
| 6.2.8 | 2024-08-12 | [43753](https://github.com/airbytehq/airbyte/pull/43753) | Update dependencies |
| 6.2.7 | 2024-08-10 | [43570](https://github.com/airbytehq/airbyte/pull/43570) | Update dependencies |
| 6.2.6 | 2024-08-03 | [43102](https://github.com/airbytehq/airbyte/pull/43102) | Update dependencies |
| 6.2.5 | 2024-07-27 | [42682](https://github.com/airbytehq/airbyte/pull/42682) | Update dependencies |
| 6.2.4 | 2024-07-20 | [42367](https://github.com/airbytehq/airbyte/pull/42367) | Update dependencies |
| 6.2.3 | 2024-07-13 | [41848](https://github.com/airbytehq/airbyte/pull/41848) | Update dependencies |
| 6.2.2 | 2024-07-10 | [41467](https://github.com/airbytehq/airbyte/pull/41467) | Update dependencies |
| 6.2.1 | 2024-07-09 | [41180](https://github.com/airbytehq/airbyte/pull/41180) | Update dependencies |
| 6.2.0 | 2024-07-07 | [39935](https://github.com/airbytehq/airbyte/pull/39935) | Update CDK to 2.0. |
| 6.1.6 | 2024-07-06 | [40956](https://github.com/airbytehq/airbyte/pull/40956) | Update dependencies |
| 6.1.5 | 2024-06-25 | [40426](https://github.com/airbytehq/airbyte/pull/40426) | Update dependencies |
| 6.1.4 | 2024-06-21 | [39935](https://github.com/airbytehq/airbyte/pull/39935) | Update dependencies |
| 6.1.3 | 2024-06-04 | [39029](https://github.com/airbytehq/airbyte/pull/39029) | [autopull] Upgrade base image to v1.2.1 |
| 6.1.2 | 2024-06-03 | [38831](https://github.com/airbytehq/airbyte/pull/38831) | Bump CDK to allow and prefer versions `1.x` |
| 6.1.1 | 2024-05-20 | [38256](https://github.com/airbytehq/airbyte/pull/38256) | Replace AirbyteLogger with logging.Logger |
| 6.1.0 | 2024-04-08 | [36898](https://github.com/airbytehq/airbyte/pull/36898) | Update car prices and years |
| 6.0.3 | 2024-03-15 | [36167](https://github.com/airbytehq/airbyte/pull/36167) | Make 'count' an optional config parameter. |
| 6.0.2 | 2024-02-12 | [35174](https://github.com/airbytehq/airbyte/pull/35174) | Manage dependencies with Poetry. |
| 6.0.1 | 2024-02-12 | [35172](https://github.com/airbytehq/airbyte/pull/35172) | Base image migration: remove Dockerfile and use the python-connector-base image |
| 6.0.0 | 2024-01-30 | [34644](https://github.com/airbytehq/airbyte/pull/34644) | Declare 'id' columns as primary keys. |
| 5.0.2 | 2024-01-17 | [34344](https://github.com/airbytehq/airbyte/pull/34344) | Ensure unique state messages |
| 5.0.1 | 2023-01-08 | [34033](https://github.com/airbytehq/airbyte/pull/34033) | Add standard entrypoints for usage with AirbyteLib |
| 5.0.0 | 2023-08-08 | [29213](https://github.com/airbytehq/airbyte/pull/29213) | Change all `*id` fields and `products.year` to be integer |
| 4.0.0 | 2023-07-19 | [28485](https://github.com/airbytehq/airbyte/pull/28485) | Bump to test publication |
| 3.0.2 | 2023-07-07 | [28060](https://github.com/airbytehq/airbyte/pull/28060) | Bump to test publication |
| 3.0.1 | 2023-06-28 | [27807](https://github.com/airbytehq/airbyte/pull/27807) | Fix bug with purchase stream updated_at |
| 3.0.0 | 2023-06-23 | [27684](https://github.com/airbytehq/airbyte/pull/27684) | Stream cursor is now `updated_at` & remove `records_per_sync` option |
| 2.1.0 | 2023-05-08 | [25903](https://github.com/airbytehq/airbyte/pull/25903) | Add user.address (object) |
| 2.0.3 | 2023-02-20 | [23259](https://github.com/airbytehq/airbyte/pull/23259) | bump to test publication |
| 2.0.2 | 2023-02-20 | [23259](https://github.com/airbytehq/airbyte/pull/23259) | bump to test publication |
| 2.0.1 | 2023-01-30 | [22117](https://github.com/airbytehq/airbyte/pull/22117) | `source-faker` goes beta |
| 2.0.0       | 2022-12-14 | [20492](https://github.com/airbytehq/airbyte/pull/20492) and [20741](https://github.com/airbytehq/airbyte/pull/20741) | Decouple stream states for better parallelism                                                                   |
| 1.0.0       | 2022-11-28 | [19490](https://github.com/airbytehq/airbyte/pull/19490)                                                              | Faker uses the CDK; rename streams to be lower-case (breaking), add determinism to random purchases, and rename |
| 0.2.1       | 2022-10-14 | [19197](https://github.com/airbytehq/airbyte/pull/19197)                                                              | Emit `AirbyteEstimateTraceMessage`                                                                              |
| 0.2.0       | 2022-10-14 | [18021](https://github.com/airbytehq/airbyte/pull/18021)                                                              | Move to mimesis for speed!                                                                                      |
| 0.1.8       | 2022-10-12 | [17889](https://github.com/airbytehq/airbyte/pull/17889)                                                              | Bump to test publish command (2)                                                                                |
| 0.1.7       | 2022-10-11 | [17848](https://github.com/airbytehq/airbyte/pull/17848)                                                              | Bump to test publish command                                                                                    |
| 0.1.6       | 2022-09-07 | [16418](https://github.com/airbytehq/airbyte/pull/16418)                                                              | Log start of each stream                                                                                        |
| 0.1.5       | 2022-06-10 | [13695](https://github.com/airbytehq/airbyte/pull/13695)                                                              | Emit timestamps in the proper ISO format                                                                        |
| 0.1.4       | 2022-05-27 | [13298](https://github.com/airbytehq/airbyte/pull/13298)                                                              | Test publication flow                                                                                           |
| 0.1.3       | 2022-05-27 | [13248](https://github.com/airbytehq/airbyte/pull/13248)                                                              | Add options for records_per_sync and page_size                                                                  |
| 0.1.2       | 2022-05-26 | [13293](https://github.com/airbytehq/airbyte/pull/13293)                                                              | Test publication flow                                                                                           |
| 0.1.1       | 2022-05-26 | [13235](https://github.com/airbytehq/airbyte/pull/13235)                                                              | Publish for AMD and ARM (M1 Macs) & remove User.birthdate                                                       |
| 0.1.0       | 2022-04-12 | [11738](https://github.com/airbytehq/airbyte/pull/11738)                                                              | The Faker Source is created                                                                                     |

</details>
