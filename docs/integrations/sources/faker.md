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

| Version | Date       | Pull Request                                             | Subject                     |
| :------ | :--------- | :------------------------------------------------------- | :-------------------------- |
| 0.1.0   | 2022-04-12 | [11738](https://github.com/airbytehq/airbyte/pull/11738) | The Faker Source is created |
