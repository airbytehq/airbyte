# Documentation and Docusaurus

We use [docusaurus](https://docusaurus.io) for consistent process, in `Airbyte` **no website is generated**.
Functionally this is a very fancy **linter**

Running the build process will **check for broken links**, please read the output and address
any broken links that you are able to do.

## Installation

For consistency across other Airbyte projects we use yarn (A Javascript based software package manager)

```bash
brew install yarn

cd docusaurus
yarn install
yarn build
```

At this point you will see any broken links that docusaurus was able to find.

## Developing Locally

```bash
yarn start # any changes will automatically be reflected in your browser!
```

## Making Changes

All the content for docs.airbyte.com lives in the `/docs` directory in this repo. All files are markdown. Make changes or add new files, and you should see them in your browser!

If you have created any new files, be sure to add them manually to the table of contents found here in this [file](https://github.com/airbytehq/airbyte/blob/master/docusaurus/sidebars.js)

## Plugin Client Redirects

A silly name, but a useful plugin that adds redirect functionality to docusaurus
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

## Deploying Docs

We use Github Pages for hosting this docs website, and [Docusaurus](https://docusaurus.io/) as the docs framework. Any change to the `/docs` directory you make is deployed when you merge to your PR to the master branch automagically!

The source code for the docs lives in the [airbyte monorepo's `docs/` directory](https://github.com/airbytehq/airbyte/tree/master/docs). Any changes to the `/docs` directory will be tested automatically in your PR. Be sure that you wait for the tests to pass before merging! If there are CI problems publishing your docs, you can run `tools/bin/deploy_docusaurus` locally - this is the publish script that CI runs.
