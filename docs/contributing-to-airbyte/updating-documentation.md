# Updating Documentation

Our documentation uses [GitBook](https://gitbook.com), and all the [Markdown](https://guides.github.com/features/mastering-markdown/) files are stored in our Github repository.

## Workflow for updating docs

1. Modify docs using Git or the Github UI (All docs live in the `docs/` folder in the [Airbyte repository](https://github.com/airbytehq/airbyte))
2. If you're adding new files, update `docs/SUMMARY.md`.
3. If you're moving existing pages, add redirects in the [`.gitbook.yaml` file](https://github.com/airbytehq/airbyte/blob/master/.gitbook.yaml) in the Airbyte repository root directory
4. Create a Pull Request

### Modify in the Github UI
1. Directly edit the docs you want to edit [in the Github UI](https://docs.github.com/en/github/managing-files-in-a-repository/managing-files-on-github/editing-files-in-your-repository)
2. Create a Pull Request

### Modify using Git

1. [Fork](https://docs.github.com/en/github/getting-started-with-github/fork-a-repo) the repository.
2. Clone the fork on your workstation:

   ```bash
   git clone git@github.com:{YOUR_USERNAME}/airbyte.git
   cd airbyte
   ```
   Or
   ```bash
   git clone https://github.com/{YOUR_USERNAME}/airbyte.git
   cd airbyte
   ```
   {% hint style="info" %}
   While cloning on Windows, you might encounter errors about long filenames. Refer to the instructions [here](../deploying-airbyte/local-deployment.md#handling-long-filename-error) to correct it.
   {% endhint %}

3. Modify the documentation.
4. Create a pull request

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
* development pre-requisites (like which language or binaries are required for development)
* how to install dependencies
* how to build and run the code locally & via Docker
* any other information needed for local iteration
  
### Changelogs

##### Core
Core changelogs should be updated in the `docs/project-overview/platform.md` file.

#### Connectors
Each connector should have a CHANGELOG.md section in its public facing docs in the `docs/integrations/<sources OR destinations>/<name>` at the bottom of the page. Inside, each new connector version should have a section whose title is the connector's version number. The body of this section should describe the changes added in the new version. For example: 

```
| Version | Date       | Pull Request | Subject |
| :------ | :--------  | :-----       | :------ |
| 0.2.0   | 20XX-05-XX | [PR2#](https://github.com/airbytehq/airbyte/pull/PR2#) | Fixed bug with schema generation <br><br> Added a better description for the `password` input parameter |
| 0.1.0   | 20XX-04-XX | [PR#](https://github.com/airbytehq/airbyte/pull/PR#) | Added incremental sync |
```
  
### Source code comments
It's hard to pin down exactly what to do around source code comments, but there are two (very subjective) and rough guidelines: 

**If something is not obvious, write it down**. Examples include:

* non-trivial class definitions should have docstrings
* magic variables should have comments explaining why those values are used (e.g: if using a page size of 10 in a connector, describe why if possible. If there is no reason, that's also fine, just mention in a comment). 
* Complicated subroutines/logic which cannot be refactored should have comments explaining what they are doing and why
    
**If something is obvious, don't write it down** since it's probably more likely to go out of date. For example, a comment like `x = 42; // sets x to 42` is not adding any new information and is therefore better omitted. 

###  Issues & Pull Requests

#### Titles

**Describe outputs, not implementation**: An issue or PR title should describe the desired end result, not the implementation. The exception is child issues/subissues of an epic. 
**Be specific about the domain**. Airbyte operates a monorepo, so being specific about what is being changed in the PR or issue title is important. 

Some examples: 
_subpar issue title_: `Remove airbyteCdk.dependsOn("unrelatedPackage")`. This describes a solution not a problem.

_good issue title_: `Building the Airbyte Python CDK should not build unrelated packages`. Describes desired end state and the intent is understandable without reading the full issue. 

_subpar PR title_: `Update tests`. Which tests? What was the update?
  
_good PR title_: `Source MySQL: update acceptance tests to connect to SSL-enabled database`. Specific about the domain and change that was made. 

**PR title conventions**
When creating a PR, follow the naming conventions depending on the change being made: 

* Notable updates to Airbyte Core: "🎉<description of feature>"
    * e.g: `🎉 enable configuring un-nesting in normalization`
* New connectors: “🎉 New source or destination: <name>” e.g: `🎉 New Source: Okta`
* New connector features: “🎉<Source or Destination> <name>: <feature description> E.g:
    * `🎉 Destination Redshift: write JSONs as SUPER type instead of VARCHAR`
    * `🎉 Source MySQL: enable logical replication`
* Bugfixes should start with the  🐛 emoji
    * `🐛 Source Facebook Marketing: fix incorrect parsing of lookback window`
* Documentation improvements should start with any of the book/paper emojis: 📚 📝 etc…
*  Any refactors, cleanups, etc.. that are not visible improvements to the user should not have emojis

The emojis help us identify which commits should be included in the product release notes. 

#### Descriptions 
**Context**: Provide enough information (or a link to enough information) in the description so team members with no context can understand what the issue or PR is trying to accomplish. This usually means you should include two things: 

1. Some background information motivating the problem
2. A description of the problem itself
3. Good places to start reading and file changes that can be skipped
Some examples: 

_insufficient context_: `Create an OpenAPI to JSON schema generator`. Unclear what the value or problem being solved here is. 

_good context_:
```
When creating or updating connectors, we spend a lot of time manually transcribing JSON Schema files based on OpenAPI docs. This is ncessary because OpenAPI and JSON schema are very similar but not perfectly compatible. This process is automatable. Therefore we should create a program which converts from OpenAPI to JSONSchema format.
``` 
