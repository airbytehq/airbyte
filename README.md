# Getting Started

 ![GitHub Workflow Status](https://img.shields.io/github/workflow/status/datalineio/dataline/Dataline%20CI) ![License](https://img.shields.io/github/license/datalineio/dataline)

![](docs/.gitbook/assets/dataline_light-background%20%281%29.svg)

**Data integration made simple, secure and reliable**  
The new open-source standard to sync data from applications & databases to warehouses.

[![](https://dataline.io/wp-content/uploads/2020/08/Deploy-with-Docker.png)](https://docs.dataline.io/deployment/deploying-dataline)

![](https://dataline.io/wp-content/uploads/2020/08/Sources_List.png)

Dataline is on a mission to make data integration pipelines a commodity.

* **Maintenance-free connectors you can use in minutes**. Just authenticate your sources and warehouse, and get connectors that adapts to schema and API changes for you.
* On a mission to **cover the long tail of integrations**, as Dataline will be very active in maintaining the pipelines’ reliability. 
* **Building new integrations made trivial**. We make it very easy to add new integrations that you need, by offering scheduling and orchestration. 
* **Your data stays in your cloud**. Have full control over your data, and the costs of your data transfers. 
* **No more security compliance process** to go through as self-hosted. 
* **No more pricing indexed on volume**, as cloud-based solutions offer. 

The new open-source standard for data integration engine that syncs data from applications & databases to warehouses.

## Getting Started

### Quick start

```bash
docker-compose up
```

Now go to [http://localhost:8000](http://localhost:8000)

### Update images

```bash
docker-compose -f docker-compose.build.yaml build
docker-compose -f docker-compose.build.yaml push
```

## Features

* **Normalized schemas**: Elegant, entirely customizable and a fully extensible admin panel.
* **Full-grade scheduler**: Automate your replications with the frequency you need.
* **Real-time Monitoring**: We log all errors to let you know about them.
* **Incremental updates**: Automated replications are based on incremental updates to reduce your data transfer costs.
* **Manual full refresh**: Sometimes, you need to re-sync all your data to start again.
* **Granular system logs**: No opacity whatsoever to let you control and trust.

[See more on our website.](https://dataline.io/features/)

## Contributing

We love contributions to Dataline, big or small. See our [Contributing Guide](https://docs.dataline.io/contributing/contributing-to-dataline) on how to get started. Not sure where to start? We’ve listed some [good first issues](https://github.com/datalineio/dataline/labels/good%20first%20issue) to start with. You can also [book a free, no-pressure pairing session](http://drift.me/johnlafleur) with one of our core contributors.

## Community support

For general help using Dataline, please refer to the official Dataline documentation. For additional help, you can use one of these channels to ask a question:

* [Slack](https://join.slack.com/t/datalineusers/shared_invite/zt-gj10ijyq-ZcUVTnUJWpD4eKICy0RU2A) \(For live discussion with the Community and Dataline team\)
* [GitHub](https://github.com/datalineio/dataline) \(Bug reports, Contributions\)
* [Twitter](https://twitter.com/datalinehq) \(Get the news fast\)

## Roadmap

Check out our [roadmap](https://github.com/datalineio/dataline/projects/1) to get informed of the latest features released and the upcoming ones. You may also give us insights and vote for a specific feature. For our high-level roadmap and strategy, you can check [our handbook](https://docs.dataline.io/company-handbook/company-handbook/roadmap).

## License

Dataline is licensed under the MIT license. See the [LICENSE](https://docs.dataline.io/license) file for licensing information.

