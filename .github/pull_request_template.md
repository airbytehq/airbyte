## What
*Describe what the change is solving*
*It helps to add screenshots if it affects the frontend.*

## How
*Describe the solution*

## Recommended reading order
1. `x.java`
2. `y.python`

## 🚨 User Impact 🚨
*Are there any breaking changes? What is the end result perceived by the user?*

*For connector PRs, use this section to explain which type of semantic versioning bump occurs as a result of the changes. Refer to our [Semantic Versioning for Connectors](https://docs.airbyte.com/contributing-to-airbyte/#semantic-versioning-for-connectors) guidelines for more information. **Breaking changes to connectors must be documented by an Airbyte engineer (PR author, or reviewer for community PRs) by using the [Breaking Change Release Playbook](https://docs.google.com/document/d/1VYQggHbL_PN0dDDu7rCyzBLGRtX-R3cpwXaY8QxEgzw/edit).***

*If there are breaking changes, please merge this PR with the 🚨🚨 emoji so changelog authors can further highlight this if needed.*


## Pre-merge Actions
*Expand the relevant checklist and delete the others.*

<details><summary><strong>New Connector</strong></summary>

### Community member or Airbyter

- **Community member?** Grant edit access to maintainers ([instructions](https://docs.github.com/en/github/collaborating-with-pull-requests/working-with-forks/allowing-changes-to-a-pull-request-branch-created-from-a-fork#enabling-repository-maintainer-permissions-on-existing-pull-requests))
- Unit & integration tests added and passing. Community members, please provide proof of success locally e.g: screenshot or copy-paste unit, integration, and acceptance test output. To run acceptance tests for a Python connector, follow instructions in the README. For java connectors run `./gradlew :airbyte-integrations:connectors:<name>:integrationTest`.
- Connector version is set to `0.0.1`
    - `Dockerfile` has version `0.0.1`
- Documentation updated
    - Connector's `README.md`
    - Connector's `bootstrap.md`. See [description and examples](https://docs.google.com/document/d/1ypdgmwmEHWv-TrO4_YOQ7pAJGVrMp5BOkEVh831N260/edit?usp=sharing)
    - `docs/integrations/<source or destination>/<name>.md` including changelog with an entry for the initial version. See changelog [example](https://docs.airbyte.io/integrations/sources/stripe#changelog)
    - `docs/integrations/README.md`

### Airbyter

If this is a community PR, the Airbyte engineer reviewing this PR is responsible for the below items.

- Create a non-forked branch based on this PR and test the below items on it
- Build is successful
- If new credentials are required for use in CI, add them to GSM. [Instructions](https://docs.airbyte.io/connector-development#using-credentials-in-ci).

</details>

<details><summary><strong>Updating a connector</strong></summary>

### Community member or Airbyter

- Grant edit access to maintainers ([instructions](https://docs.github.com/en/github/collaborating-with-pull-requests/working-with-forks/allowing-changes-to-a-pull-request-branch-created-from-a-fork#enabling-repository-maintainer-permissions-on-existing-pull-requests))
- Unit & integration tests added


### Airbyter

If this is a community PR, the Airbyte engineer reviewing this PR is responsible for the below items.

- Create a non-forked branch based on this PR and test the below items on it
- Build is successful
- If new credentials are required for use in CI, add them to GSM. [Instructions](https://docs.airbyte.io/connector-development#using-credentials-in-ci).

</details>

<details><summary><strong>Connector Generator</strong></summary>

- Issue acceptance criteria met
- PR name follows [PR naming conventions](https://docs.airbyte.com/contributing-to-airbyte/issues-and-pull-requests#pull-request-title-convention)
- If adding a new generator, add it to the [list of scaffold modules being tested](https://github.com/airbytehq/airbyte/blob/master/airbyte-integrations/connector-templates/generator/build.gradle#L41)
- The generator test modules (all connectors with `-scaffold` in their name) have been updated with the latest scaffold by running `./gradlew :airbyte-integrations:connector-templates:generator:testScaffoldTemplates` then checking in your changes
- Documentation which references the generator is updated as needed

</details>
