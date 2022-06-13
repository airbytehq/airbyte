# Deploying and Reverting Docs

![docs are fun](../assets/docs/docs.jpg)

Docusaurus has a strange deployment pattern.  Luckily that pattern is abstracted away from you.

If you were looking for the contribution guide [check this doc out](contributing_to_docs.md)

Docs will deploy from whatever branch you are in. You will probably want to deploy from master, but that is at your discretion.

[This is the deployment tool](https://github.com/airbytehq/airbyte/blob/master/tools/bin/deploy_docusaurus)
You will need a github ssh key, the tool will properly tell you if you don't have one though

At it's simplest just open the airbyte repo and run `./tools/bin/deploy_docusaurus`

A typical deployment will look like this


```bash
cd airbyte
# or cd airbyte-cloud  
git checkout master
git pull
./tools/bin/deploy_docusaurus
```

If docs has a problem this procedure will work the same on older branches.
The push to production is a force push so collisions are unlikely

If you want to revert/rollback it will look something like this

```bash
cd airbyte
git checkout $SOME_OLDER_BRANCH
./tools/bin/deploy_docusaurus
```
