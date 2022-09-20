# Updating Documentation

We welcome contributions to the Airbyte documentation! 

Our docs are written in [Markdown](https://guides.github.com/features/mastering-markdown/) following the [Google developer documentation style guide](https://developers.google.com/style/highlights) and the files are stored in our [Github repository](https://github.com/airbytehq/airbyte/tree/master/docs). The docs are published at [docs.airbyte.com](https://docs.airbyte.com/) using [Docusaurus](https://docusaurus.io/) and [GitHub Pages](https://pages.github.com/). 

## Finding good first issues

The Docs team maintains a list of [#good-first-issues](https://github.com/airbytehq/airbyte/issues?q=is%3Aopen+is%3Aissue+label%3Aarea%2Fdocumentation+label%3A%22good+first+issue%22) for new contributors. 

- If you're new to technical writing, start with the smaller issues (fixing typos, broken links, spelling and grammar, and so on). You can [edit the files directly on GitHub](#editing-directly-on-github).
- If you're an experienced technical writer or a developer interested in technical writing, comment on an issue that interests you to discuss it with the Docs team. Once we decide on the approach and the tasks involved, [edit the files and open a Pull Request](#editing-on-your-local-machine) for the Docs team to review.

## Contributing to Airbyte docs

Before contributing to Airbyte docs, read the Airbyte Community [Code of Conduct](code-of-conduct.md)

:::tip
If you're new to GitHub and Markdown, complete [the First Contributions tutorial](https://github.com/firstcontributions/first-contributions) and learn [Markdown basics](https://guides.github.com/features/mastering-markdown/) before contributing to Airbyte documentation. 
:::

You can contribute to Airbyte docs in two ways:

### Editing directly on GitHub

To make minor changes (example: fixing typos) or edit a single file, you can edit the file directly on GitHub:

1. Click **Edit this page** at the bottom of any published document on [docs.airbyte.com](https://docs.airbyte.com/). You'll be taken to the GitHub editor. 
2. [Edit the file directly on GitHub and open a Pull Request](https://docs.github.com/en/repositories/working-with-files/managing-files/editing-files).

### Editing on your local machine

To make complex changes or edit multiple files, edit the files on your local machine:

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

3. Test changes locally: 

  Run the following commands in your terminal:

  ```bash
  cd docusaurus
  yarn install
  yarn build
  yarn serve
  ```
  Then navigate to [http://localhost:3000/](http://localhost:3000/) to see your changes. You can stop the running server in OSX/Linux by pressing `Ctrl-C` in the terminal.

4. [Follow the GitHub workflow](https://docs.github.com/en/get-started/quickstart/contributing-to-projects/) to edit the files and create a pull request.

    :::note
    Before we accept any contributions, you'll need to sign the Contributor License Agreement (CLA). By signing a CLA, we can ensure that the community is free and confident in its ability to use your contributions. You will be prompted to sign the CLA while opening a pull request.
    :::

5. Assign `airbytehq/docs` as a Reviewer for your pull request. 

## Additional guidelines

- If you're updating a connector doc, follow the [Connector documentation template](https://hackmd.io/Bz75cgATSbm7DjrAqgl4rw)
- If you're adding a new file, update the [sidebars.js file](https://github.com/airbytehq/airbyte/blob/master/docusaurus/sidebars.js)
- If you're adding a README to a code module, make sure the README has the following components:
    - A brief description of the module
    - Development pre-requisites (like which language or binaries are required for development)
    - How to install dependencies
    - How to build and run the code locally & via Docker
    - Any other information needed for local iteration

## Advanced tasks 

### Adding a redirect

To add a redirect, open the [`docusaurus.config.js`](https://github.com/airbytehq/airbyte/blob/master/docusaurus/docusaurus.config.js#L22) file and locate the following commented section:

```js
//                        {
//                         from: '/some-lame-path',
//                         to: '/a-much-cooler-uri',
//                        },
```

Copy this section, replace the values, and [test the changes locally](#editing-on-your-local-machine) by going to the path you created a redirect for and verify that the address changes to the new one.

:::note 
Your path **needs* a leading slash `/` to work
:::

### Deploying and reverting the documentation site

:::note
Only the Airbyte team and maintainers have permissions to deploy the documentation site.
:::

You'll need a GitHub SSH key to deploy the documentation site using the [deployment tool](https://github.com/airbytehq/airbyte/blob/master/tools/bin/deploy_docusaurus). 

To deploy the documentation site, run:

```bash
cd airbyte
# or cd airbyte-cloud  
git checkout master
git pull
./tools/bin/deploy_docusaurus
```

To revert/rollback doc changes, run:

```
cd airbyte
git checkout <OLDER_BRANCH>
./tools/bin/deploy_docusaurus
```
