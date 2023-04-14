# PyPI

This page guides you through the process of setting up the PyPI source connector.

## Setup guide
### Get package name from PyPI
This is the name given in `pip install package_name` box. For example, `airbyte-cdk` is the package name for [airbyte-cdk](https://pypi.org/project/airbyte-cdk/).

Optianlly, provide a version name. If not provided, the release stream, containing data for particular version, cannot be used. The project stream is as same as release stream but contains data for all versions.

## Supported streams and sync modes

* [Project](https://warehouse.pypa.io/api-reference/json.html#project)
* [Release](https://warehouse.pypa.io/api-reference/json.html#release)
* [Stats](https://warehouse.pypa.io/api-reference/stats.html)

### Performance considerations

Due to the heavy caching and CDN use, there is currently no rate limiting of PyPI APIs at the edge.

In addition, PyPI reserves the right to temporarily or permanently prohibit a consumer based on irresponsible activity.

Try not to make a lot of requests (thousands) in a short amount of time (minutes). Generally PyPI can handle it, but it’s preferred to make requests in serial over a longer amount of time if possible.

## Changelog

| Version | Date       | Pull Request                                             | Subject         |
|:--------|:-----------|:---------------------------------------------------------|:----------------|
| 0.1.0   | 2022-10-29 | [18632](https://github.com/airbytehq/airbyte/pull/18632) | Initial Release |


