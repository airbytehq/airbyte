# Faker

## Sync overview

The Faker source generates sample data using the python [`faker`](https://faker.readthedocs.io/) package. Specifically, we generate data that looks like an e-commerce company's `users` table with the [`faker.profile()`](https://faker.readthedocs.io/en/master/providers/faker.providers.profile.html) method.

### Output schema

Only `Users` is supported.

### Data type mapping

Native Airbyte types (string, number, date, etc)

### Features

| Feature           | Supported?\(Yes/No\) | Notes |
| :---------------- | :------------------- | :---- |
| Full Refresh Sync | Yes                  |       |
| Incremental Sync  | Yes                  |       |
| Namespaces        | No                   |       |

Of note, if you choose `Incremental Sync`, state will be maintained between syncs, and once you hit `count` records, no new records will be added.
You can choose a specific `seed` (integer) as an option for this connector which will guarantee that the same fake records are generated each time. Otherwise, random data will be created on each subsequent sync.

### Rate Limiting & Performance Considerations

N/A

## Getting started

### Requirements

None!

### Setup guide

N/A

## Changelog

| Version | Date       | Pull Request                                             | Subject                                                   |
| :------ | :--------- | :------------------------------------------------------- | :-------------------------------------------------------- |
| 0.2.0   | 2022-10-14 | [18021](https://github.com/airbytehq/airbyte/pull/18021)     | Move to mimesis for speed!                                |
| 0.1.8   | 2022-10-12 | [17889](https://github.com/airbytehq/airbyte/pull/17889) | Bump to test publish command (2)                          |
| 0.1.7   | 2022-10-11 | [17848](https://github.com/airbytehq/airbyte/pull/17848) | Bump to test publish command                              |
| 0.1.6   | 2022-09-07 | [16418](https://github.com/airbytehq/airbyte/pull/16418) | Log start of each stream                                  |
| 0.1.5   | 2022-06-10 | [13695](https://github.com/airbytehq/airbyte/pull/13695) | Emit timestamps in the proper ISO format                  |
| 0.1.4   | 2022-05-27 | [13298](https://github.com/airbytehq/airbyte/pull/13298) | Test publication flow                                     |
| 0.1.3   | 2022-05-27 | [13248](https://github.com/airbytehq/airbyte/pull/13248) | Add options for records_per_sync and page_size            |
| 0.1.2   | 2022-05-26 | [13248](https://github.com/airbytehq/airbyte/pull/13293) | Test publication flow                                     |
| 0.1.1   | 2022-05-26 | [13235](https://github.com/airbytehq/airbyte/pull/13235) | Publish for AMD and ARM (M1 Macs) & remove User.birthdate |
| 0.1.0   | 2022-04-12 | [11738](https://github.com/airbytehq/airbyte/pull/11738) | The Faker Source is created                               |
