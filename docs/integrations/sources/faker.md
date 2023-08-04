# Faker

## Sync overview

The Sample Data (Faker) source generates sample data using the python [`mimesis`](https://mimesis.name/en/master/) package.

### Output schema

This source will generate an "e-commerce-like" dataset with users, products, and purchases. Here's what is produced at a Postgres destination connected to this source:

```sql
CREATE TABLE "public"."users" (
    "address" jsonb,
    "occupation" text,
    "gender" text,
    "academic_degree" text,
    "weight" int8,
    "created_at" timestamptz,
    "language" text,
    "telephone" text,
    "title" text,
    "updated_at" timestamptz,
    "nationality" text,
    "blood_type" text,
    "name" text,
    "id" float8,
    "age" int8,
    "email" text,
    "height" text,
    -- "_airbyte_ab_id" varchar,
    -- "_airbyte_emitted_at" timestamptz,
    -- "_airbyte_normalized_at" timestamptz,
    -- "_airbyte_users_hashid" text
);

CREATE TABLE "public"."users_address" (
    "_airbyte_users_hashid" text,
    "country_code" text,
    "province" text,
    "city" text,
    "street_number" text,
    "state" text,
    "postal_code" text,
    "street_name" text,
    -- "_airbyte_ab_id" varchar,
    -- "_airbyte_emitted_at" timestamptz,
    -- "_airbyte_normalized_at" timestamptz,
    -- "_airbyte_address_hashid" text
);

CREATE TABLE "public"."products" (
    "id" float8,
    "make" text,
    "year" float8,
    "model" text,
    "price" float8,
    "created_at" timestamptz,
    -- "_airbyte_ab_id" varchar,
    -- "_airbyte_emitted_at" timestamptz,
    -- "_airbyte_normalized_at" timestamptz,
    -- "_airbyte_dev_products_hashid" text,
);

CREATE TABLE "public"."purchases" (
    "id" float8,
    "user_id" float8,
    "product_id" float8,
    "purchased_at" timestamptz,
    "added_to_cart_at" timestamptz,
    "returned_at" timestamptz,
    -- "_airbyte_ab_id" varchar,
    -- "_airbyte_emitted_at" timestamptz,
    -- "_airbyte_normalized_at" timestamptz,
    -- "_airbyte_dev_purchases_hashid" text,
);

```

### Features

| Feature           | Supported?\(Yes/No\) | Notes |
| :---------------- | :------------------- | :---- |
| Full Refresh Sync | Yes                  |       |
| Incremental Sync  | Yes                  |       |
| Namespaces        | No                   |       |

Of note, if you choose `Incremental Sync`, state will be maintained between syncs, and once you hit `count` records, no new records will be added.

You can choose a specific `seed` (integer) as an option for this connector which will guarantee that the same fake records are generated each time. Otherwise, random data will be created on each subsequent sync.

### Requirements

None!

## Changelog

| Version | Date       | Pull Request                                                                                                          | Subject                                                                                                         |
|:--------|:-----------|:----------------------------------------------------------------------------------------------------------------------|:----------------------------------------------------------------------------------------------------------------|
| 4.0.0   | 2023-07-19 | [28485](https://github.com/airbytehq/airbyte/pull/28485)                                                              | Bump to test publication                                                                                        |
| 3.0.2   | 2023-07-07 | [27807](https://github.com/airbytehq/airbyte/pull/28060)                                                              | Bump to test publication                                                                                        |
| 3.0.1   | 2023-06-28 | [27807](https://github.com/airbytehq/airbyte/pull/27807)                                                              | Fix bug with purchase stream updated_at                                                                         |
| 3.0.0   | 2023-06-23 | [27684](https://github.com/airbytehq/airbyte/pull/27684)                                                              | Stream cursor is now `updated_at` & remove `records_per_sync` option                                            |
| 2.1.0   | 2023-05-08 | [25903](https://github.com/airbytehq/airbyte/pull/25903)                                                              | Add user.address (object)                                                                                       |
| 2.0.3   | 2023-02-20 | [23259](https://github.com/airbytehq/airbyte/pull/23259)                                                              | bump to test publication                                                                                        |
| 2.0.2   | 2023-02-20 | [23259](https://github.com/airbytehq/airbyte/pull/23259)                                                              | bump to test publication                                                                                        |
| 2.0.1   | 2023-01-30 | [22117](https://github.com/airbytehq/airbyte/pull/22117)                                                              | `source-faker` goes beta                                                                                        |
| 2.0.0   | 2022-12-14 | [20492](https://github.com/airbytehq/airbyte/pull/20492) and [20741](https://github.com/airbytehq/airbyte/pull/20741) | Decouple stream states for better parallelism                                                                   |
| 1.0.0   | 2022-11-28 | [19490](https://github.com/airbytehq/airbyte/pull/19490)                                                              | Faker uses the CDK; rename streams to be lower-case (breaking), add determinism to random purchases, and rename |
| 0.2.1   | 2022-10-14 | [19197](https://github.com/airbytehq/airbyte/pull/19197)                                                              | Emit `AirbyteEstimateTraceMessage`                                                                              |
| 0.2.0   | 2022-10-14 | [18021](https://github.com/airbytehq/airbyte/pull/18021)                                                              | Move to mimesis for speed!                                                                                      |
| 0.1.8   | 2022-10-12 | [17889](https://github.com/airbytehq/airbyte/pull/17889)                                                              | Bump to test publish command (2)                                                                                |
| 0.1.7   | 2022-10-11 | [17848](https://github.com/airbytehq/airbyte/pull/17848)                                                              | Bump to test publish command                                                                                    |
| 0.1.6   | 2022-09-07 | [16418](https://github.com/airbytehq/airbyte/pull/16418)                                                              | Log start of each stream                                                                                        |
| 0.1.5   | 2022-06-10 | [13695](https://github.com/airbytehq/airbyte/pull/13695)                                                              | Emit timestamps in the proper ISO format                                                                        |
| 0.1.4   | 2022-05-27 | [13298](https://github.com/airbytehq/airbyte/pull/13298)                                                              | Test publication flow                                                                                           |
| 0.1.3   | 2022-05-27 | [13248](https://github.com/airbytehq/airbyte/pull/13248)                                                              | Add options for records_per_sync and page_size                                                                  |
| 0.1.2   | 2022-05-26 | [13248](https://github.com/airbytehq/airbyte/pull/13293)                                                              | Test publication flow                                                                                           |
| 0.1.1   | 2022-05-26 | [13235](https://github.com/airbytehq/airbyte/pull/13235)                                                              | Publish for AMD and ARM (M1 Macs) & remove User.birthdate                                                       |
| 0.1.0   | 2022-04-12 | [11738](https://github.com/airbytehq/airbyte/pull/11738)                                                              | The Faker Source is created                                                                                     |
