# Deploying and Reverting Docs

![docs are fun](../assets/docs/docs.jpg)

We use Github Pages for hosting this docs website, and Docusaurus as the docs framework. Docusaurus has a strange deployment pattern. Luckily that pattern is abstracted away from you.

The source code for the docs lives in the [airbyte monorepo's `docs/` directory](https://github.com/airbytehq/airbyte/tree/master/docs). To publish the updated docs on this website after you've committed a change to the `docs/` markdown files, it is required to locally run a manual publish flow.

Docs will deploy from whatever branch you are in. You will probably want to deploy from master, but that is at your discretion.

[This is the deployment tool](https://github.com/airbytehq/airbyte/blob/master/tools/bin/deploy_docusaurus). You will need a github ssh key, the tool will properly tell you if you don't have one though

At it's simplest just open the airbyte repo and run `./tools/bin/deploy_docusaurus`

A typical deployment will look like this

```bash
cd airbyte
# or cd airbyte-cloud
git checkout master
git pull
./tools/bin/deploy_docusaurus
```

If docs has a problem this procedure will work the same on older branches. The push to production is a force push so collisions are unlikely

If you want to revert/rollback it will look something like this

```bash
cd airbyte
git checkout $SOME_OLDER_BRANCH
./tools/bin/deploy_docusaurus
```

Automating this process via CI is currently not easy because we push to a [dedicated repo hosting the Github pages](https://airbytehq.github.io) from the `airbyte` monorepo, which is hard to do in CI. This is not intended to be the end state (we will need to publish these docs via CI eventually), but as of May 2022 have decided the juice isn't worth the squeeze just yet.
