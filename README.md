<p align="center">
  <a href="https://airbyte.com"><img src="https://assets.website-files.com/605e01bc25f7e19a82e74788/624d9c4a375a55100be6b257_Airbyte_logo_color_dark.svg" alt="Airbyte"></a>
</p>
<p align="center">
    <em>Open-source data movement for ELT pipelines and AI agents — from APIs, databases & files to warehouses, lakes, and AI applications</em>
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
<a href="https://www.youtube.com/c/AirbyteHQ/?sub_confirmation=1" target="_blank">
    <img alt="YouTube Channel Views" src="https://img.shields.io/youtube/channel/views/UCQ_JWEFzs1_INqdhIO3kmrw?style=social">
</a>
<a href="https://github.com/airbytehq/airbyte/actions/workflows/gradle.yml" target="_blank">
    <img src="https://img.shields.io/github/actions/workflow/status/airbytehq/airbyte/gradle.yml?branch=master" alt="Build">
</a>
<a href="https://github.com/airbytehq/airbyte/tree/master/docs/project-overview/licenses" target="_blank">
    <img src="https://img.shields.io/static/v1?label=license&message=MIT&color=white" alt="License">
</a>
<a href="https://github.com/airbytehq/airbyte/tree/master/docs/project-overview/licenses" target="_blank">
    <img src="https://img.shields.io/static/v1?label=license&message=ELv2&color=white" alt="License">
</a>
</p>

We believe that only an **open-source solution to data movement** can cover the long tail of data sources while empowering data engineers to customize existing connectors. Our ultimate vision is to help you move data from any source to any destination — whether that destination is a data warehouse, a data lake, or an AI agent through the Airbyte MCP. Airbyte provides a [catalog](https://docs.airbyte.com/integrations/) of 700+ connectors for APIs, databases, data warehouses, data lakes, and AI applications.

![Airbyte Connections UI](https://github.com/airbytehq/airbyte/assets/38087517/35b01d0b-00bf-407b-87e6-a5cd5cd720b5)
_Screenshot taken from [Airbyte Cloud](https://cloud.airbyte.com/signup)_.

### Getting Started

- **Move and sync data.** Deploy [Airbyte Core](https://docs.airbyte.com/quickstart/deploy-airbyte) or [sign up for Airbyte Cloud](https://cloud.airbyte.com/signup) and follow the [Cloud getting started guide](https://docs.airbyte.com/cloud/getting-started-with-airbyte-cloud). Choose from [700+ connectors](https://docs.airbyte.com/integrations/) for APIs, databases, warehouses, lakes, and other data systems.

- **Work with Airbyte from your AI agent through the Airbyte MCP.** Your AI agent (Claude, ChatGPT, Cursor, VS Code Copilot, and many others) can build and manage data pipelines, troubleshoot syncs, read logs, and answer questions about Airbyte. Start with the [overview](https://docs.airbyte.com/platform/airbyte-mcp); for Airbyte Cloud, connect to the hosted server at `https://mcp.airbyte.com/mcp` and sign in with OAuth using the [Cloud setup guide](https://docs.airbyte.com/platform/airbyte-mcp/install). For Airbyte Core deployments, the [self-managed setup](https://docs.airbyte.com/platform/airbyte-mcp/self-managed) runs locally against your deployment's API. See the available [tools](https://docs.airbyte.com/platform/airbyte-mcp/tools).

- **Call APIs and search data directly (Airbyte Cloud only).** Through the [context layer](https://docs.airbyte.com/platform/context-layer), AI agents can read live data from supported sources and query supported destinations such as BigQuery and Snowflake without waiting for a sync, and search your data. This is available only in Airbyte Cloud; direct reads are read-only.

- **Build connectors and orchestrate pipelines.** Create connectors with the [no-code Connector Builder](https://docs.airbyte.com/connector-development/connector-builder-ui/overview) or [low-code CDK](https://docs.airbyte.com/connector-development/config-based/low-code-cdk-overview), and explore popular use cases in our [tutorials](https://airbyte.com/tutorials). Orchestrate Airbyte syncs with [Airflow](https://docs.airbyte.com/operator-guides/using-the-airflow-airbyte-operator), [Dagster](https://docs.airbyte.com/operator-guides/using-dagster-integration), [Kestra](https://docs.airbyte.com/operator-guides/using-kestra-plugin), or the [Airbyte API](https://reference.airbyte.com/). You can also do this through the Airbyte MCP: your AI agent can publish and update custom connector manifests, run and cancel syncs, and change connection schedules.

Try it out yourself with our [demo app](https://demo.airbyte.io/), visit our [full documentation](https://docs.airbyte.com/), and learn more about [recent announcements](https://airbyte.com/blog-categories/company-updates). See our [registry](https://connectors.airbyte.com/files/generated_reports/connector_registry_report.html) for a full list of connectors already available in Airbyte or Airbyte Cloud.

### Join the Airbyte Community

The Airbyte community can be found in the [Airbyte Community Slack](https://airbyte.com/community), where you can ask questions and voice ideas. You can also ask for help in our [Airbyte Forum](https://github.com/airbytehq/airbyte/discussions). Airbyte's roadmap is publicly viewable on [GitHub](https://github.com/orgs/airbytehq/projects/37/views/1?pane=issue&itemId=26937554).

For videos and blogs on data engineering and building your data stack, check out Airbyte's [Content Hub](https://airbyte.com/content-hub), [YouTube](https://www.youtube.com/c/AirbyteHQ), and sign up for our [newsletter](https://airbyte.com/newsletter).

### Contributing

If you've found a problem with Airbyte, please open a [GitHub issue](https://github.com/airbytehq/airbyte/issues/new/choose). To contribute to Airbyte and see our Code of Conduct, please see the [contributing guide](https://docs.airbyte.com/contributing-to-airbyte/). We have a list of [good first issues](https://github.com/airbytehq/airbyte/labels/contributor-program) that contain bugs that have a relatively limited scope. This is a great place to get started, gain experience, and get familiar with our contribution process.

#### PR Permission Requirements

When submitting a pull request, please ensure that Airbyte maintainers have write access to your branch. This allows us to apply formatting fixes and dependency updates directly, significantly speeding up the review and approval process.

To enable write access on your PR from Airbyte maintainers, please check the "Allow edits from maintainers" box when submitting from your PR. You must also create your PR from a fork in your **personal GitHub account** rather than an organization account, or else you will not see this option. The requirement to create from your personal fork is based on GitHub's additional security restrictions for PRs created from organization forks. For more information about the GitHub security model, please see the [GitHub documentation page regarding PRs from forks](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/working-with-forks/allowing-changes-to-a-pull-request-branch-created-from-a-fork).

For more details on contribution requirements, please see our [contribution workflow documentation](https://docs.airbyte.com/platform/contributing-to-airbyte#standard-contribution-workflow).

### Security

Airbyte takes security issues very seriously. **Please do not file GitHub issues or post on our public forum for security vulnerabilities**. If you believe you have uncovered a vulnerability, read the vulnerability disclosure policy for the affected product and report it as described on [Report a security vulnerability](https://airbyte.com/security/vdp).

[Airbyte Enterprise](https://airbyte.com/airbyte-enterprise) also offers additional security features (among others) on top of Airbyte open-source.

### License

See the [LICENSE](docs/LICENSE) file for licensing information, and our [FAQ](https://docs.airbyte.com/platform/developer-guides/licenses/license-faq) for any questions you may have on that topic.

### Thank You

Airbyte would not be possible without the support and assistance of other open-source tools and companies! Visit our [thank you page](THANK-YOU.md) to learn more about how we build Airbyte.

<a href="https://github.com/airbytehq/airbyte/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=airbytehq/airbyte"/>
</a>
