---
description: Working with Airbyte Platform
---

# Overview

In order to facilitate faster development workflows, airbytehq/airbyte was split into two repositories on 2023-19-02:

- airbytehq/airbyte connectors and development around
- airbytehq/airbyte-platform the codebase that facilitates connectors
- airbytehq/airbyte-protocol used by both connectors and platform, the underlying protocol that airbyte uses to perform data transfers

If you have an existing pull request in airbytehq/airbyte that should instead target airbyte-platform there are two ways that you can move it over

# Migrating from airbytehq/airbyte

1. Using our /create-platform-pr [slash command tool](https://github.com/airbytehq/airbyte/blob/master/.github/workflows/create-oss-pr-snapshot.yml) for platform. Simply comment "create-platform-pr" on your existing airbytehq/airbyte pull request and let our automation perform the migration for you. Note that if there are any conflicts between files, for the purposes of simplicity the tool will always use your version of the file in the pull request vs the version that exists in airbyte-platform.
2. Manually migrate your pull request. If you have a pull request that is touching both connectors and platform code, for instance, you may need to perform this step manually. The steps to do so are below:

- First, fork airbyte-platform:


Let's start with the name of your branch on airbytehq/airbyte, called my-old-pr-branch. First, add airbyte-platform as a new remote in airbytehq/airbyte, and add your new fork as well as a remote.

```bash
cd airbyte
git remote add platform git@github.com:airbytehq/airbyte-platform.git
git remote add platform-fork git@github.com:my-github-username/airbyte-platform.git
```

- check out main and create a new branch from airbyte-platform main for your pull request in airbyte-platform

```bash
git fetch platform main 
git checkout main 
git checkout -b my-new-pr-branch
```

- check out your old pr branch and get the commits that need to be carried over
```bash
git checkout my-old-pr-branch 
git log
```
Copy each commit SHA that you need to pull over. Example:

```bash
commit f1bab07d25a118e0f347869e6bc8b3820ba757e4 (HEAD -> master, origin/master, origin/HEAD)
Author: Conor <cpdeethree@users.noreply.github.com>
Date:   Mon Feb 20 08:29:48 2023 -0600

    remove airbyte-commons-temporal/worker-models (#23239)
    
    * remove airbyte-commons-temporal
    
    * remove airbyte-worker-models

```

In this case you want "f1bab07d25a118e0f347869e6bc8b3820ba757e4"

Then, checkout my-new-pr-branch again and cherry-pick the commit(s) you want over to my-new-pr-branch

```bash
git checkout my-new-pr-branch 
git cherry-pick f1bab07d25a118e0f347869e6bc8b3820ba757e4
```

Finally, once all your commits have been brought over, you can push your new branch up to your airbyte-platform fork and open a new pull request 

```bash
git push platform-fork my-new-pr-branch
```
