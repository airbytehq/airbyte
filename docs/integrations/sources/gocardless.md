# GoCardless

## Overview

The GoCardless source can sync data from the [GoCardless API](https://gocardless.com/)

#### Output schema

This source is capable of syncing the following streams:

- Mandates
- Payments
- Payouts
- Refunds

#### Features

| Feature                   | Supported? |
| :------------------------ | :--------- |
| Full Refresh Sync         | Yes        |
| Incremental - Append Sync | No         |
| Namespaces                | No         |

### Requirements / Setup Guide

- Access Token
- GoCardless Environment
- GoCardless Version
- Start Date

## Changelog

| Version | Date       | Pull Request                                             | Subject                                   |
| :------ | :--------- | :------------------------------------------------------- | :---------------------------------------- |
| 0.1.0   | 2022-10-19 | [17792](https://github.com/airbytehq/airbyte/pull/17792) | Initial release supporting the GoCardless |
