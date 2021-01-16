# HTTP Request

## Overview

This source allows you to make any http request an Airbyte source! On each sync, this source makes a single http request to the provided URL. Whatever json body is returned is written to the destination.

#### Output schema

It contains one stream: `data`. That stream will contain one record which is the json blob returned by the http request.

#### Data type mapping

`data` is a json blob.

#### Features

| Feature | Supported? |
| :--- | :--- |
| Full Refresh Sync | Yes |
| Incremental Sync | Coming soon |

### Getting started

#### Setup guide

Provide a url, http\_method, \(optional\) headers, \(optional\) request body. The source will make exactly this http request.

