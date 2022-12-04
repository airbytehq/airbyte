# Documentation and Docusaurus

We use [docusaurus](https://docusaurus.io) for consitent process, in `Airbyte` **no website is generated**.
Functionally this is a very fancy **linter**

Running the build process will **check for broken links**, please read the output and address
any broken links that you are able to do.

# Installation

For consistency across other Airbyte projects we use yarn (A Javascript based software package manager)

```bash
brew install yarn

cd docusaurus
yarn install
yarn build
```

At this point you will see any broken links that docusaurus was able to find.

# Pull requests

This is all just markdown at the end of the day so open a PR against master like any other commit.

# Local website
If you want to run the docs as a docusaurus site locally just run `yarn run build`.
Url will show on successful command execution.


# Future

If we ever do want to host these documents outside the repo this convention should allow us to stand up a documentation website very quickly
