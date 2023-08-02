# Connector generator

This module generates code to bootstrap your connector development. 

## Getting started

### Using NPM

```bash
npm install
npm run generate
```

### Using Docker
If you don't want to install `npm` you can run the generator using Docker: 

```
./generate.sh
```

## Contributions

### Testing connector templates
To test that the templates generate valid code, we follow a slightly non-obvious strategy. Since the templates 
themselves do not contain valid Java/Python/etc.. syntax, we can't build them directly. 
At the same time, due to the way Gradle works (where phase 1 is "discovering" all the projects that need to be 
built and phase 2 is running the build), it's not very ergonomic to have one Gradle task generate a module
from each template, build it in the same build lifecycle, then remove it. 

So we use the following strategy: 

1. Locally, generate an empty connector using the generator module  (call the generated connector something like `java-jdbc-scaffolding`)
1. Check the generated module into source control

Then, [in CI](https://github.com/airbytehq/airbyte/blob/master/.github/workflows/gradle.yml), we test two invariants: 

1. There is no diff between the checked in module, and a module generated during using the latest version of the templater
1. The checked in module builds successfully

Together, these two invariants guarantee that the templates produce a valid module. 

The way this is performed is as follows: 

1. [in CI ](https://github.com/airbytehq/airbyte/blob/master/.github/workflows/gradle.yml) we trigger the task `:airbyte-integrations:connector-templates:generator:testScaffoldTemplates`. This task deletes the checked in `java-jdbc-scaffolding`. Then the task generates a fresh instance of the module with the same name `java-jdbc-scaffolding`. 
1. We run a `git diff`. If there is a diff, then fail the build (this means the latest version of the templates produce code which has not been manually reviewed by someone who checked them in intentionally). Steps 1 & 2 test the first invariant. 
1. Separately, in `settings.gradle`, the `java-jdbc-scaffolding` module is registered as a java submodule. This causes it to be built as part of the normal build cycle triggered in CI. If the generated code does not compile for whatever reason, the build will fail on building the `java-jdbc-scaffolding` module. 
