# DoubleVerify

## Overview

The DoubleVerify source provides the output of the streams mentioned below. The streams have DV client's DV measurement data and verification data for the tag based and social campaigns. It supports both Full Refresh and Incremental syncs. 

### Output schema

DoubleVerify connector outputs the following streams:

* Facebook
* Pinterest
* Snapchat
* Twitter
* Youtube
* BrandSafety
* Fraud
* GeoReport
* Viewability

### Features

| Feature | Supported? |
| :--- | :--- |
| Full Refresh Sync | Yes |
| Incremental - Append Sync | Yes |


## Getting started

### Requirements

* DoubleVerify user account - assigned to at least one DV Reporting Program
* Access to the DV Pinnacle platform

### Token generation guide

- Login to DV Pinnacle platform
- Navigate to the Analytics dropdown menu
- Either select 'Data API' for Standard, GroupM Billable and DV Authentic Attention® Report Request Types or 'Data API - Legacy' for Social Platforms Report Request Types
- Select Create Token
- Choose the Reporting Programs you want token for
- Select create to create token
- Copy the access token and provide it to the DoubleVerify connector

Note: New access token must be geenrated if the current one is lost or not copied

## Changelog

| Version | Date | Pull Request | Subject |
| 0.0.1   | 2023-06-12 | [27251](https://github.com/airbytehq/airbyte/pull/27251) | Introduce Doubleverify API source 