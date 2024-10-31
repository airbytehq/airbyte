# Documentation and Docusaurus

We use [Docusaurus](https://docusaurus.io) to build Airbyte's
[documentation site](https://docs.airbyte.io) from documentation source files in Markdown, and lint
the source files. We host the resulting docs site on Vercel. It deploys automatically when any
changes get merged to `master`.

## Installation

For consistency across other Airbyte projects we use `pnpm` (A Javascript based software package
manager).

```bash
brew install pnpm

cd docusaurus
pnpm install
pnpm build
```

`pnpm build` will build Docusaurus site in `docusaurus/build` directory.

## Developing Locally

If you want to make changes to the documentation, you can run docusaurus locally in a way that would
listen to any source docs changes and live-reload them:

```bash
pnpm start # any changes will automatically be reflected in your browser!
```

All the content for docs.airbyte.com lives in the `/docs` directory in this repo. All files are
markdown. Make changes or add new files, and you should see them in your browser!

## Changing Navigation Structure

If you have created any new files, be sure to add them manually to the table of contents found here
in [`sidebars.js`](https://github.com/airbytehq/airbyte/blob/master/docusaurus/sidebars.js)

## Contributing

We welcome documentation updates! If you'd like to contribute a change, please make sure to:

- Run `pnpm build` and check that all build steps are successful.
- Run `pnpm prettier . -w`.
- Push your changes into a pull request, and follow the PR template instructions.

When you make a pull request, Vercel will automatically build a test instance of the full docs site
and link it in the pull request for review.

### Checking for broken links

Airbyte's docs site checks links with Docusaurus at build time, and with an additional GitHub action
periodically:

- Running the build process will **check for broken links**, please read the output and address any
  broken links that you are able to do.

> [!NOTE] Docusaurus links checker only checks _relative_ links, and assumes that absolute links are
> fine. For that reason, if you're linking to another Airbyte documentation page, make it a relative
> link. I.e. `[link](/connector-development/overview.md)` instead of
> `[link](https://docs.airbyte.com/connector-development/)`. That way, if your link breaks in the
> future due to a navigation restructure, it will be caught with `pnpm build`.

## Docusaurus Plugins We Use

### Plugin Client Redirects

A silly name, but a useful plugin that adds redirect functionality to docusaurus
[Official documentation here](https://docusaurus.io/docs/api/plugins/@docusaurus/plugin-client-redirects)

If you're proposing to move an existing documentation file or change its name, please setup a
redirect rule.

You will need to edit
[this docusaurus file](https://github.com/airbytehq/airbyte/blob/master/docusaurus/docusaurus.config.js#L22)

You will see a commented section the reads something like this

```js
//                        {
//                         from: '/some-lame-path',
//                         to: '/a-much-cooler-uri',
//                        },
```

Copy this section, replace the values, and [test it locally](locally_testing_docusaurus.md) by going
to the path you created a redirect for and checked to see that the address changes to your new one.

_Note:_ Your path \*_needs_ a leading slash `/` to work

## Deploying Docs

Airbyte docs live on Vercel. Any change to the `/docs` directory you make is deployed when you merge
to your PR to the master branch automagically!

The source code for the docs lives in the
[airbyte monorepo's `docs/` directory](https://github.com/airbytehq/airbyte/tree/master/docs). Any
changes to the `/docs` directory will be tested automatically in your PR. Be sure that you wait for
the tests to pass before merging! If there are CI problems publishing your docs, you can run
`tools/bin/deploy_docusaurus` locally - this is the publish script that CI runs.
