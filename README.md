# Overview

![GitHub Workflow Status](https://img.shields.io/github/workflow/status/airbytehq/airbyte/Airbyte%20CI) ![License](https://img.shields.io/github/license/airbytehq/airbyte)

![](docs/.gitbook/assets/airbyte_horizontal_color_white-background.svg)

**Data integration made simple, secure and extensible.**  
The new open-source standard to sync data from applications, APIs & databases to warehouses.

[![](docs/.gitbook/assets/deploy-locally.svg)](docs/deploying-airbyte/on-your-workstation.md) [![](docs/.gitbook/assets/deploy-on-aws.svg)](docs/deploying-airbyte/on-aws-ec2.md) [![](docs/.gitbook/assets/deploy-on-gcp.svg)](docs/deploying-airbyte/on-gcp-compute-engine.md)

![](docs/.gitbook/assets/airbyte-ui-for-your-integration-pipelines.png)

Airbyte is on a mission to make data integration pipelines a commodity.

* **Maintenance-free connectors you can use in minutes**. Just authenticate your sources and warehouse, and get connectors that adapt to schema and API changes for you.
* **Building new connectors made trivial.** We make it very easy to add new connectors that you need, using the language of your choice, by offering scheduling and orchestration. 
* Designed to **cover the long tail of connectors and needs**. Benefit from the community's battle-tested connectors and adapt them to your specific needs.
* **Your data stays in your cloud**. Have full control over your data, and the costs of your data transfers. 
* **No more security compliance process** to go through as Airbyte is self-hosted. 
* **No more pricing indexed on volume**, as cloud-based solutions offer. 

Here's a list of our [connectors with their health status](docs/integrations/connector-health.md).

## Quick start

```bash
git clone https://github.com/airbytehq/airbyte.git
cd airbyte
docker-compose up
```

Now visit [http://localhost:8000](http://localhost:8000)

Here is a [step-by-step guide](docs/getting-started.md) showing you how to load data from an API into a file, all on your computer.

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

**Also, we will never ask you to maintain your connector. The goal is that the Airbyte team and the community helps maintain it, let's call it crowdsourced maintenance!**

## Community support

For general help using Airbyte, please refer to the official Airbyte documentation. For additional help, you can use one of these channels to ask a question:

* [Slack](https://slack.airbyte.io) \(For live discussion with the Community and Airbyte team\)
* [GitHub](https://github.com/airbytehq/airbyte) \(Bug reports, Contributions\)
* [Twitter](https://twitter.com/airbytehq) \(Get the news fast\)
* [Weekly office hours](https://airbyte.io/weekly-office-hours/) \(Live informal 30-minute video call sessions with the Airbyte team\)

## Roadmap

Check out our [roadmap](docs/roadmap.md) to get informed on what we are currently working on, and what we have in mind for the next weeks, months and years.

## License

Airbyte is licensed under the MIT license. See the [LICENSE](docs/license.md) file for licensing information.

