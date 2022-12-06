<p align="center">
  <a href="https://airbyte.com"><img src="https://assets.website-files.com/605e01bc25f7e19a82e74788/624d9c4a375a55100be6b257_Airbyte_logo_color_dark.svg" alt="Airbyte"></a>
</p>
<p align="center">
    <em>Data integration platform for ELT pipelines from APIs, databases & files to databases, warehouses & lakes</em>
</p>
<p align="center">
<a href="https://github.com/airbytehq/airbyte/stargazers/" target="_blank">
    <img src="https://img.shields.io/github/stars/airbytehq/airbyte?style=social&label=Star&maxAge=2592000" alt="Test">
</a>
<a href="https://github.com/airbytehq/airbyte/releases" target="_blank">
    <img src="https://img.shields.io/github/v/release/airbytehq/airbyte?color=white" alt="Release">
</a>
<a href="https://airbytehq.slack.com/" target="_blank">
    <img src="https://img.shields.io/badge/slack-join-white.svg?logo=slack" alt="Slack">
</a>
<a href="https://github.com/airbytehq/airbyte/actions/workflows/gradle.yml" target="_blank">
    <img src="https://img.shields.io/github/workflow/status/airbytehq/airbyte/Airbyte%20CI" alt="Build">
</a>
<a href="https://github.com/airbytehq/airbyte/tree/a9b1c6c0420550ad5069aca66c295223e0d05e27/LICENSE/README.md" target="_blank">
    <img src="https://img.shields.io/static/v1?label=license&message=MIT&color=white" alt="License">
</a>
<a href="https://github.com/airbytehq/airbyte/tree/a9b1c6c0420550ad5069aca66c295223e0d05e27/LICENSE/README.md" target="_blank">
    <img src="https://img.shields.io/static/v1?label=license&message=ELv2&color=white" alt="License">
</a>
</p>

We believe that only an open-source solution to data movement can cover the long-tail of connectors while empowering data engineers to customize existing connectors. Airbyte connectors take the form of a Docker image which follows the Airbyte specification and can be implemented in any language. You can replicate data from any source to any destination. We provide a low-code Conector Development Kit (CDK) for API connectors, a Python CDK and Java templates to quickly create new connectors.

Airbyte comes with a built-in scheduler and Temporal to orchestrate workers. Airbyte normalizes extracted data with dbt models and can trigger custom transformation in SQL and dbt. You can also orchestrate Airbyte syncs with Airflow, Prefect and Dagster.

![Airbyte OSS Connections UI](https://user-images.githubusercontent.com/2302748/205949986-5207ca24-f1f0-41b1-97e1-a0745a0de55a.png)

Check [300+ connectors](https://docs.airbyte.com/integrations/) for APIs, databases, warehouses and lakes.

## Quick start

### Run Airbyte locally

You can run Airbyte locally with Docker.

```bash
git clone https://github.com/airbytehq/airbyte.git
cd airbyte
docker-compose up
```

Login to the web app at [http://localhost:8000](http://localhost:8000) by entering the defeault credentials found in your .env file.

```
BASIC_AUTH_USERNAME=airbyte
BASIC_AUTH_PASSWORD=password
```

Follow the instructions on the web app UI to setup a source, destination and connection to replicate data. Connections support the most popular sync modes: full refresh, incremental and change data capture for databases.

Read the [Airbyte docs](https://docs.airbyte.com).

### Manage Airbyte configurations with code

You can also programmatically manage sources, destinations and connections with YAML files, [Octavia CLI](https://github.com/airbytehq/airbyte/tree/master/octavia-cli), and API.

### Deploy Airbyte to production

Deployment options: [Docker](https://docs.airbyte.com/deploying-airbyte/local-deployment), [AWS EC2](https://docs.airbyte.com/deploying-airbyte/on-aws-ec2), [Azure](https://docs.airbyte.com/deploying-airbyte/on-azure-vm-cloud-shell), [GCP](https://docs.airbyte.com/deploying-airbyte/on-gcp-compute-engine), [Kubernetes](https://docs.airbyte.com/deploying-airbyte/on-kubernetes), [Restack](https://docs.airbyte.com/deploying-airbyte/on-restack), [Plural](https://docs.airbyte.com/deploying-airbyte/on-plural), [Oracle Cloud](https://docs.airbyte.com/deploying-airbyte/on-oci-vm), [Digital Ocean](https://docs.airbyte.com/deploying-airbyte/on-digitalocean-droplet)...

### Sign up for Airbyte Cloud

Airbyte Cloud is the fastest and most reliable way to run Airbyte. You can get started with free credits in minutes.

Sign up for [Airbyte Cloud](https://cloud.airbyte.io/signup).

## Contributing

Get started by checking Github issues and creating a Pull Request. An easy way to start contributing is to update an existing connector or create a new connector using the low-code and Python CDKs. You can find the code for existing connectors in the [connectors](https://github.com/airbytehq/airbyte/tree/master/airbyte-integrations/connectors) directory. The Airbyte platform is written in Java and the frontend in React. You can also contribute to our docs and tutorials. 

The Airbyte team is here to help get your contributions merged. Advanced Airbyte users can apply to the [Maintainer program](https://airbyte.com/maintainer-program) and [Writer Program](https://airbyte.com/write-for-the-community). 

Read the [Contributing guide](docs/contributing-to-airbyte/README.md).

## Resources

- [Weekly office hours](https://airbyte.io/weekly-office-hours/) for live informal sessions with the Airbyte team
- [Slack](https://slack.airbyte.io) for quick discussion with the Community and Airbyte team
- [Discourse](https://discuss.airbyte.io/) for deeper conversations about features, connectors, and problems
- [GitHub](https://github.com/airbytehq/airbyte) for code, issues and pull requests
- [Youtube](https://www.youtube.com/c/AirbyteHQ) for videos on data engineering
- [Newsletter](https://airbyte.com/newsletter) for product updates and data news
- [Blog](https://airbyte.com/blog) for data insigts articles, tutorials and updates
- [Docs](https://docs.airbyte.com/) for Airbyte features

## Reporting vulnerabilities

⚠️ Please do not file GitHub issues or post on our public forum for security vulnerabilities as they are public! ⚠️

Airbyte takes security issues very seriously. If you have any concerns about Airbyte or believe you have uncovered a vulnerability, please get in touch via the e-mail address security@airbyte.io. In the message, try to provide a description of the issue and ideally a way of reproducing it. The security team will get back to you as soon as possible.

Note that this security address should be used only for undisclosed vulnerabilities. Dealing with fixed issues or general questions on how to use the security features should be handled regularly via the user and the dev lists. Please report any security problems to us before disclosing it publicly.

## Roadmap

Check out our [roadmap](https://app.harvestr.io/roadmap/view/pQU6gdCyc/launch-week-roadmap) to get informed on what we are currently working on, and what we have in mind for the next weeks, months, and years.

## License

See the [LICENSE](docs/project-overview/licenses/) file for licensing information, and our [FAQ](docs/project-overview/licenses/license-faq.md) for any questions you may have on that topic.
