# Changelog

## 0.1.15
Add \_limit and \_page_size as internal config parameters for SAT

## 0.1.14
If the input config file does not comply with spec schema, raise an exception instead of `system.exit`.

## 0.1.13
Fix defect with user defined backoff time retry attempts, number of retries logic fixed

## 0.1.12
Add raise_on_http_errors, max_retries, retry_factor properties to be able to ignore http status errors and modify retry time in HTTP stream

## 0.1.11
Add checking specified config againt spec for read, write, check and discover commands

## 0.1.10
Add `MultipleTokenAuthenticator` class to allow cycling through a list of API tokens when making HTTP requests

## 0.1.8
Allow to fetch primary key info from singer catalog

## 0.1.7
Allow to use non-JSON payloads in request body for http source

## 0.1.6
Add abstraction for creating destinations.

Fix logging of the initial state.

## 0.1.5
Allow specifying keyword arguments to be sent on a request made by an HTTP stream: https://github.com/airbytehq/airbyte/pull/4493

## 0.1.4
Allow to use Python 3.7.0: https://github.com/airbytehq/airbyte/pull/3566

## 0.1.2
Fix an issue that caused infinite pagination: https://github.com/airbytehq/airbyte/pull/3366

## 0.1.1
Initial Release
