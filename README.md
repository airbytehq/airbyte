![GitHub Workflow Status](https://img.shields.io/github/workflow/status/datalineio/dataline/Dataline%20CI) ![License](https://img.shields.io/github/license/datalineio/dataline)

<p align="center">
  <a href="https://dataline.io">
    <img src="https://dataline.io/wp-content/uploads/2020/08/Dataline_light-background.svg" width="318px" alt="Dataline logo" />
  </a>
</p>

<h3 align="center">Data integration made simple, secure and reliable.</h3>
<p align="center">The new open-source standard to sync data from applications & databases to warehouses.</p>
<br />
<p align="center">
  <a href="https://docs.dataline.io/deployment/deploying-dataline/with-docker">
    <img src="https://dataline.io/wp-content/uploads/2020/09/Deploy-Locally.svg"  />
  </a>

<a href="https://docs.dataline.io/deployment/deploying-dataline/on-aws-ec2">
<img src="https://dataline.io/wp-content/uploads/2020/09/Deploy-on-AWS.svg" />
</a>

<a href="https://docs.dataline.io/deployment/deploying-dataline/on-gcp-compute-engine">
<img src="https://dataline.io/wp-content/uploads/2020/09/Deploy-on-GCP.svg" />
</a>
</p>
<br />

![](https://dataline.io/wp-content/uploads/2020/08/Sources_List.png)

<br>

Dataline is on a mission to make data integration pipelines a commodity.

- **Maintenance-free connectors you can use in minutes**. Just authenticate your sources and warehouse, and get connectors that adapts to schema and API changes for you.
- On a mission to **cover the long tail of integrations**, as Dataline will be very active in maintaining the pipelines’ reliability. 
- **Building new integrations made trivial**. We make it very easy to add new integrations that you need, by offering scheduling and orchestration. 
- **Your data stays in your cloud**. Have full control over your data, and the costs of your data transfers. 
- **No more security compliance process** to go through as self-hosted. 
- **No more pricing indexed on volume**, as cloud-based solutions offer. 

## Getting Started

### Quick start

```bash
git clone git@github.com:datalineio/dataline.git
cd dataline
docker-compose up
```

Now go to [http://localhost:8000](http://localhost:8000)

### Update images

```bash
docker-compose -f docker-compose.build.yaml build
docker-compose -f docker-compose.build.yaml push
```

## Features

- **Normalized schemas**: Elegant, entirely customizable and a fully extensible admin panel.
- **Full-grade scheduler**: Automate your replications with the frequency you need.
- **Real-time Monitoring**: We log all errors to let you know about them.
- **Incremental updates**: Automated replications are based on incremental updates to reduce your data transfer costs.
- **Manual full refresh**: Sometimes, you need to re-sync all your data to start again.
- **Granular system logs**: No opacity whatsoever to let you control and trust.

<a href="https://dataline.io/features/">See more on our website.</a>

## Contributing

We love contributions to Dataline, big or small. See our <a href="https://docs.dataline.io/contributing/contributing-to-dataline">Contributing Guide</a> on how to get started.
Not sure where to start? We’ve listed some <a href="https://github.com/datalineio/dataline/labels/good%20first%20issue">good first issues</a> to start with. You can also <a href="http://drift.me/micheltricot/meeting">book a free, no-pressure pairing session</a> with one of our core contributors.
 
## Community support

For general help using Dataline, please refer to the official Dataline documentation. For additional help, you can use one of these channels to ask a question:
- <a href="https://join.slack.com/t/datalineusers/shared_invite/zt-gj10ijyq-ZcUVTnUJWpD4eKICy0RU2A">Slack</a> (For live discussion with the Community and Dataline team)
- <a href="https://github.com/datalineio/dataline">GitHub</a> (Bug reports, Contributions)
- <a href="https://twitter.com/datalinehq">Twitter</a> (Get the news fast)
 
## Roadmap

Check out our <a href="https://github.com/datalineio/dataline/projects/1">roadmap</a> to get informed of the latest features released and the upcoming ones. You may also give us insights and vote for a specific feature.
For our high-level roadmap and strategy, you can check <a href="https://docs.dataline.io/company-handbook/company-handbook/roadmap">our handbook</a>.

## License

Dataline is licensed under the MIT license. See the <a href="https://docs.dataline.io/license">LICENSE</a> file for licensing information.
