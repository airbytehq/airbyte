# Introduction

[![GitHub stars](https://img.shields.io/github/stars/airbytehq/airbyte?style=social&label=Star&maxAge=2592000)](https://GitHub.com/airbytehq/airbyte/stargazers/) [![GitHub Workflow Status](https://img.shields.io/github/workflow/status/airbytehq/airbyte/Airbyte%20CI)](https://github.com/airbytehq/airbyte/actions/workflows/gradle.yml) [![License](https://img.shields.io/static/v1?label=license&message=MIT&color=brightgreen)](https://github.com/airbytehq/airbyte/tree/a9b1c6c0420550ad5069aca66c295223e0d05e27/LICENSE/README.md) [![License](https://img.shields.io/static/v1?label=license&message=ELv2&color=brightgreen)](https://github.com/airbytehq/airbyte/tree/a9b1c6c0420550ad5069aca66c295223e0d05e27/LICENSE/README.md)

**Data integration made simple, secure and extensible.**
The new open-source standard to sync data from applications, APIs & databases to warehouses, lakes & other destinations.

Airbyte is on a mission to make data integration pipelines a commodity.

* **Maintenance-free connectors you can use in minutes**. Just authenticate your sources and warehouse, and get connectors that adapt to schema and API changes for you.
* **Building new connectors made trivial.** We make it very easy to add new connectors that you need, using the language of your choice, by offering scheduling and orchestration. 
* Designed to **cover the long tail of connectors and needs**. Benefit from the community's battle-tested connectors and adapt them to your specific needs.
* **Your data stays in your cloud**. Have full control over your data, and the costs of your data transfers. 
* **No more security compliance process** to go through as Airbyte is self-hosted. 
* **No more pricing indexed on volume**, as cloud-based solutions offer. 

Here's a list of our [connectors with their health status](docs/integrations/).

## Quick start

```bash
git clone https://github.com/airbytehq/airbyte.git
cd airbyte
docker-compose up
```

Now visit [http://localhost:8000](http://localhost:8000)

Here is a [step-by-step guide](https://github.com/airbytehq/airbyte/tree/e378d40236b6a34e1c1cb481c8952735ec687d88/docs/quickstart/getting-started.md) showing you how to load data from an API into a file, all on your computer.

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

See our [Contributing guide](docs/contributing-to-airbyte/README.md) on how to get started. Not sure where to start? We’ve listed some [good first issues](https://github.com/airbytehq/airbyte/labels/good%20first%20issue) to start with. If you have any questions, please open a draft PR or visit our [slack channel](https://github.com/airbytehq/airbyte/tree/a9b1c6c0420550ad5069aca66c295223e0d05e27/slack.airbyte.io) where the core team can help answer your questions.

**Note that you are able to create connectors using the language you want, as Airbyte connections run as Docker containers.**

**Also, we will never ask you to maintain your connector. The goal is that the Airbyte team and the community helps maintain it, let's call it crowdsourced maintenance!**

## Community support

For general help using Airbyte, please refer to the official Airbyte documentation. For additional help, you can use one of these channels to ask a question:

* [Slack](https://slack.airbyte.io) \(For live discussion with the Community and Airbyte team\)
* [Forum](https://discuss.airbyte.io/) \(For deeper converstaions about features, connectors, or problems\)
* [GitHub](https://github.com/airbytehq/airbyte) \(Bug reports, Contributions\)
* [Twitter](https://twitter.com/airbytehq) \(Get the news fast\)
* [Weekly office hours](https://airbyte.io/weekly-office-hours/) \(Live informal 30-minute video call sessions with the Airbyte team\)

## Reporting Vulnerabilities
⚠️ Please do not file GitHub issues or post on our public forum for security vulnerabilities as they are public! ⚠️

Airbyte takes security issues very seriously. If you have any concern around Airbyte or believe you have uncovered a vulnerability, please get in touch via the e-mail address security@airbyte.io. In the message, try to provide a description of the issue and ideally a way of reproducing it. The security team will get back to you as soon as possible.

Note that this security address should be used only for undisclosed vulnerabilities. Dealing with fixed issues or general questions on how to use the security features should be handled regularly via the user and the dev lists. Please report any security problems to us before disclosing it publicly.

## Roadmap

Check out our [roadmap](https://app.harvestr.io/roadmap/view/pQU6gdCyc/launch-week-roadmap) to get informed on what we are currently working on, and what we have in mind for the next weeks, months and years.

## License

See the [LICENSE](docs/project-overview/licenses/) file for licensing information, and our [FAQ](docs/project-overview/licenses/license-faq.md) for any questions you may have on that topic.
