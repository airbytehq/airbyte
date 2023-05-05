# Welcome to Airbyte Docs

Whether you are an Airbyte user or contributor, we have docs for you!

## For Airbyte Users

### For Airbyte Cloud users

Browse the [connector catalog](https://docs.airbyte.com/integrations/) to find the connector you want. In case the connector is not yet supported on Airbyte Cloud, consider using [Airbyte Open Source](#for-airbyte-open-source-users).

Next, check out the [step-by-step tutorial](https://docs.airbyte.com/cloud/getting-started-with-airbyte-cloud) to sign up for Airbyte Cloud, understand Airbyte [concepts](https://docs.airbyte.com/cloud/core-concepts), and run your first sync. Then learn how to [use your Airbyte Cloud account](https://docs.airbyte.com/category/using-airbyte-cloud).

### For Airbyte Open Source users

Browse the [connector catalog](https://docs.airbyte.com/integrations/) to find the connector you want. If the connector is not yet supported on Airbyte Open Source, [build your own connector](https://docs.airbyte.com/connector-development/).

Next, check out the [Airbyte Open Source QuickStart](https://docs.airbyte.com/quickstart/deploy-airbyte). Then learn how to [deploy](https://docs.airbyte.com/deploying-airbyte/local-deployment) and [manage](https://docs.airbyte.com/operator-guides/upgrading-airbyte) Airbyte Open Source in your cloud infrastructure.

To get help with Airbyte deployments, check out the [Troubleshooting & FAQ](https://docs.airbyte.com/troubleshooting/), chat with Support on [Discourse](https://discuss.airbyte.io/), or join us on [Community Slack](https://slack.airbyte.io/).

### For Airbyte contributors

To contribute to Airbyte code, connectors, and documentation, refer to our [Contributing Guide](https://docs.airbyte.com/contributing-to-airbyte/).

[![GitHub stars](https://img.shields.io/github/stars/airbytehq/airbyte?style=social&label=Star&maxAge=2592000)](https://GitHub.com/airbytehq/airbyte/stargazers/) [![License](https://img.shields.io/static/v1?label=license&message=MIT&color=brightgreen)](https://github.com/airbytehq/airbyte/tree/a9b1c6c0420550ad5069aca66c295223e0d05e27/LICENSE/README.md) [![License](https://img.shields.io/static/v1?label=license&message=ELv2&color=brightgreen)](https://github.com/airbytehq/airbyte/tree/a9b1c6c0420550ad5069aca66c295223e0d05e27/LICENSE/README.md)

---

## Contributing to these docs

We welcome any contributions you have to make our docs better!

### Docs Quickstart

Assuming you have node.js installed:

```bash
cd docusaurus
yarn install # or npm install
yarn start # or npm start
# press control-c to exit the server
```

You will see changes reflected live in your browser!

### Plugin Client Redirects

A silly name, but a useful plugin that adds redirect functionality to docusuaurs
[Official documentation here](https://docusaurus.io/docs/api/plugins/@docusaurus/plugin-client-redirects)

You will need to edit [this docusaurus file](https://github.com/airbytehq/airbyte/blob/master/docusaurus/docusaurus.config.js#L22)

You will see a commented section the reads something like this

```js
//                        {
//                         from: '/some-lame-path',
//                         to: '/a-much-cooler-uri',
//                        },
```

Copy this section, replace the values, and [test it locally](locally_testing_docusaurus.md) by going to the
path you created a redirect for and checked to see that the address changes to your new one.

_Note:_ Your path \*_needs_ a leading slash `/` to work

### Deploying Docs

We use Github Pages for hosting this docs website, and [Docusaurus](https://docusaurus.io/) as the docs framework. Any change to the `/docs` directory you make is deployed when you merge to your PR to the master branch automagically!

The source code for the docs lives in the [airbyte monorepo's `docs/` directory](https://github.com/airbytehq/airbyte/tree/master/docs). Any changes to the `/docs` directory will be tested automatically in your PR. Be sure that you wait for the tests to pass before merging! If there are CI problems publishing your docs, you can run `tools/bin/deploy_docusaurus` locally - this is the publish script that CI runs.
