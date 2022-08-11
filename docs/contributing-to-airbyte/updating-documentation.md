# Updating Documentation

We welcome all contributions to the Airbyte documentation! 

Our documentation is written in [Markdown](https://guides.github.com/features/mastering-markdown/) following the [Google developer documentation style guide](https://developers.google.com/style/highlights) and the files are stored in our [Github repository](https://github.com/airbytehq/airbyte/tree/master/docs). The documentation is published at https://docs.airbyte.com/ using [Docusaurus](https://docusaurus.io/) and [GitHub Pages](https://pages.github.com/). 

:::tip
If you're new to Markdown, 
:::

## Finding open Docs issues

## How to contribute to Airbyte documentation

Before contributing to Airbyte documentation, read the Airbyte Community [Code of Conduct](code-of-conduct.md).

You can contribute to Airbyte documentation in two ways:

### Editing directly on GitHub

To make minor changes to docs (example: fixing typos) or editing a single file, you can edit the file directly on GitHub:

1. Click **Edit this page** at the bottom of on any published document on docs.airbyte.com. You'll be taken to thebGitHub editor. 
2. [Edit the file directly on GtHub and open a Pull Request](https://docs.github.com/en/repositories/working-with-files/managing-files/editing-files).

### Editing on your local machine

For complex changes or pull requests affecting multiple files, edit the files on your local machine:

1. [Fork](https://docs.github.com/en/github/getting-started-with-github/fork-a-repo) the Airbyte [repository](https://github.com/airbytehq/airbyte).
2. Clone the fork on your local machine:

   ```bash
   git clone git@github.com:{YOUR_USERNAME}/airbyte.git
   cd airbyte
   ```

   Or

   ```bash
   git clone https://github.com/{YOUR_USERNAME}/airbyte.git
   cd airbyte
   ```

   While cloning on Windows, you might encounter errors about long filenames. Refer to the instructions [here](../deploying-airbyte/local-deployment.md#handling-long-filename-error) to correct it.

3. [Follow the GitHub workflow](https://docs.github.com/en/get-started/quickstart/contributing-to-projects/) to modify the documentation and create a pull request.

:::note
Before we accept any contributions, you'll need to sign the Contributor License Agreement (CLA). By signing a CLA, we can ensure that the community is free and confident in its ability to use your contributions. You are prompted to sign the CLA during the pull request process.
:::

### Testing Changes
* You can run a copy of the website locally to test how your changes will look in production
* This is not necessary for smaller changes, but is suggested for large changes and **any** change to the sidebar, as the JSON will blow up if we misplace a comma.
* You will need [yarn](https://yarnpkg.com) installed locally to build docusaurus
* Run the following commands
```bash
cd docusaurus
yarn install
yarn build
yarn serve
```

You can now navigate to [http://localhost:3000/](http://localhost:3000/) to see your changes.  You can stop the running server in OSX/Linux by pressing `control-c` in the terminal running the server

### Deploying the docs website
We use Github Pages for hosting this docs website, and Docusaurus as the docs framework.  An [internal guide for deployment lives here](../docusaurus/deploying_and_reverting_docs.md).

The source code for the docs lives in the [airbyte monorepo's `docs/` directory](https://github.com/airbytehq/airbyte/tree/master/docs). To publish the updated docs on this website after you've committed a change to the `docs/` markdown files, it is required to locally run a manual publish flow. Locally run `./tools/bin/deploy_docusaurus` from the `airbyte` monorepo project root to deploy this docs website.

Automating this process via CI is currently not easy because we push to a [dedicated repo hosting the Github pages](https://airbytehq.github.io) from the `airbyte` monorepo, which is hard to do in CI. This is not intended to be the end state (we will need to publish these docs via CI eventually), but as of May 2022 have decided the juice isn't worth the squeeze just yet.

## Documentation Best Practices

Connectors typically have the following documentation elements:

* READMEs
* Changelogs
* Github Issues & Pull Requests
* Source code comments
* How-to guides

Below are some best practices related to each of these.

### READMEs

Every module should have a README containing:

* A brief description of the module
* development pre-requisites \(like which language or binaries are required for development\)
* how to install dependencies
* how to build and run the code locally & via Docker
* any other information needed for local iteration

### Changelogs

**Core**

Core changelogs should be updated in the `docs/project-overview/platform.md` file.

#### Connectors

Each connector should have a CHANGELOG.md section in its public facing docs in the `docs/integrations/<sources OR destinations>/<name>` at the bottom of the page. Inside, each new connector version should have a section whose title is the connector's version number. The body of this section should describe the changes added in the new version. For example:


| Version | Date       | Pull Request | Subject |
| :------ | :--------  | :-----       | :------ |
| 0.2.0   | 20XX-05-XX | [PR2#](https://github.com/airbytehq/airbyte/pull/PR2#) | Fixed bug with schema generation <br/><br/> Added a better description for the `password` input parameter|
| 0.1.0   | 20XX-04-XX | [PR#](https://github.com/airbytehq/airbyte/pull/PR#) | Added incremental sync |



