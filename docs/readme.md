# docs (by Docusaurus)

This directory contains our docs that are hosted at docs.airbyte.io.

We leverage docusaurus for documentation.  You can run the server locally by navigating to

`airbyte/docusaurus`

and running:

`yarn build && yarn serve`

This build will also happen in the cloud, however if a diff is detected the cloud test will fail

You **must** run yarn build successfully before committing your changes
