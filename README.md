# Overview

![GitHub Workflow Status](https://img.shields.io/github/workflow/status/airbytehq/airbyte/Airbyte%20CI) ![License](https://img.shields.io/github/license/airbytehq/airbyte)

![](docs/.gitbook/assets/airbyte_horizontal_dark%20%281%29%20%281%29%20%281%29.svg)

**Data integration made simple, secure and extensible.**

The new open-source standard to sync data from applications, APIs & databases to warehouses.

[![](docs/.gitbook/assets/deploy-locally%20%281%29%20%281%29%20%281%29%20%281%29%20%282%29%20%281%29%20%281%29%20%281%29%20%282%29%20%281%29%20%281%29.svg)](docs/deploying-airbyte/on-your-workstation.md) [![](docs/.gitbook/assets/deploy-on-aws%20%281%29%20%281%29%20%281%29%20%281%29%20%282%29%20%281%29%20%281%29%20%281%29%20%282%29%20%281%29%20%281%29.svg)](docs/deploying-airbyte/on-aws-ec2.md) [![](docs/.gitbook/assets/deploy-on-gcp%20%281%29%20%281%29%20%281%29%20%281%29%20%282%29%20%281%29%20%281%29%20%281%29%20%282%29%20%281%29%20%281%29.svg)](docs/deploying-airbyte/on-gcp-compute-engine.md)

![](docs/.gitbook/assets/airbyte-ui-for-your-integration-pipelines%20%281%29%20%281%29%20%281%29.png)

Airbyte is on a mission to make data integration pipelines a commodity.

* **Maintenance-free connectors you can use in minutes**. Just authenticate your sources and warehouse, and get connectors that adapt to schema and API changes for you.
* **Building new connectors made trivial.** We make it very easy to add new connectors that you need, using the language of your choice, by offering scheduling and orchestration. 
* Designed to **cover the long tail of connectors and needs**. Benefit from the community's battle-tested connectors and adapt them to your specific needs.
* **Your data stays in your cloud**. Have full control over your data, and the costs of your data transfers. 
* **No more security compliance process** to go through as Airbyte is self-hosted. 
* **No more pricing indexed on volume**, as cloud-based solutions offer. 

## Quick start

```bash
git clone https://github.com/airbytehq/airbyte.git
cd airbyte
docker-compose up
```

Now visit [http://localhost:8000](http://localhost:8000)

Here is a [step-by-step guide](docs/getting-started-tutorial.md) showing you how to load data from a sample Postgres database into another database using Airbyte, all on your computer.

## Features

* **Built for extensibility**: Adapt an existing connector to your needs or build a new one with ease.
* **Optional normalized schemas**: Entirely customizable, start with raw data or from some suggestion of normalized data.
* **Full-grade scheduler**: Automate your replications with the frequency you need.
* **Real-time monitoring**: We log all errors in full detail to help you understand.
* **Incremental updates**: Automated replications are based on incremental updates to reduce your data transfer costs.
* **Manual full refresh**: Sometimes, you need to re-sync all your data to start again.
* **Debugging autonomy**: Modify and debug pipelines as you see fit, without waiting.

[See more on our website.](https://airbyte.io/features/)

## Contributing

We love contributions to Airbyte, big or small.

See our [Contributing guide](docs/contributing-to-airbyte/) on how to get started. Not sure where to start? We’ve listed some [good first issues](https://github.com/airbytehq/airbyte/labels/good%20first%20issue) to start with. You can also [book a free, no-pressure pairing session](https://drift.me/micheltricot/meeting) with one of our core contributors.

**Note that you are able to create connectors using the language you want, as Airbyte connections run as Docker containers.**

## Community support

For general help using Airbyte, please refer to the official Airbyte documentation. For additional help, you can use one of these channels to ask a question:

* [Slack](https://slack.airbyte.io) \(For live discussion with the Community and Airbyte team\)
* [GitHub](https://github.com/airbytehq/airbyte) \(Bug reports, Contributions\)
* [Twitter](https://twitter.com/airbytehq) \(Get the news fast\)
* [Weekly office hours](https://airbyte.io/weekly-office-hours/) \(Live informal 30-minute video call sessions with the Airbyte team\)

## Roadmap

Check out our [roadmap](https://github.com/airbytehq/airbyte/projects/1) to get informed of the latest features released and the upcoming ones. You may also give us insights and vote for a specific feature. For our high-level roadmap and strategy, you can check [our handbook](docs/company-handbook/roadmap.md).

Here are some of the features we are planning on releasing:

* Incremental syncs \([\#247](https://github.com/airbytehq/airbyte/issues/247)\)
* Kubernetes support \([\#835](https://github.com/airbytehq/airbyte/issues/835)\)
* Airflow support \([\#836](https://github.com/airbytehq/airbyte/issues/836)\)
* Credential and secrets vaulting \([\#837](https://github.com/airbytehq/airbyte/issues/837)\)
* OAuth support for connector configuration \([\#768](https://github.com/airbytehq/airbyte/issues/768)\)
* Webhook connector
* Upgrade strategy
* [DBT](https://www.getdbt.com/) Integration

## License

Airbyte is licensed under the MIT license. See the [LICENSE](https://docs.airbyte.io/license) file for licensing information.

