# Breaker

The Breaker source is a special development source which allows you to configure the source in a variety of ways
and observe the results.

It currently supports the following connector issues: 
* `check` fails with a configuration error (user error)
* `check` fails due to an unexpected connector error
* `discover` fails due to an unexpected connector error

## Sync overview

The Breaker source generates sample data using the python [`mimesis`](https://mimesis.name/en/master/) package,
heavily inspired by and reusing code from `source-faker`. However, it is not meant to be as configurable as `source-faker`
with regard to what the source outputs, and is also not meant to stay up to date with features in `source-faker`.

### Output schema

This source will generate an "e-commerce-like" dataset with users, products, and purchases. 

### Features

| Feature           | Supported?\(Yes/No\) | Notes |
| :---------------- | :------------------- | :---- |
| Full Refresh Sync | Yes                  |       |
| Incremental Sync  | Yes                  |       |
| Namespaces        | No                   |       |

### Requirements

None!

## Changelog

| Version | Date       | Pull Request                                             | Subject                                                                 |
|:--------|:-----------|:---------------------------------------------------------|:------------------------------------------------------------------------|
| 0.1.0   | 2023-03-01 | [24760](https://github.com/airbytehq/airbyte/pull/24760) | Inital breaker source: configuration of breaking `check` and `discover` |
