## What
*Describe what the change is solving*
*It helps to add screenshots if it affects the frontend.*

## How
*Describe the solution*

## Recommended reading order
1. `x.java`
2. `y.python`

## Pre-merge Checklist
Expand the relevant checklist and delete the others. 

<details><summary> <strong> New Connector </strong></summary>
<p>
   
#### Community member or Airbyter
   
- [ ] **Community member?** Grant edit access to maintainers ([instructions](https://docs.github.com/en/github/collaborating-with-pull-requests/working-with-forks/allowing-changes-to-a-pull-request-branch-created-from-a-fork#enabling-repository-maintainer-permissions-on-existing-pull-requests))
- [ ] Secrets in the connector's spec are annotated with `airbyte_secret` 
- [ ] Unit & integration tests added and passing. Community members, please provide proof of success locally e.g: screenshot or copy-paste unit, integration, and acceptance test output. To run acceptance tests for a Python connector, follow instructions in the README. For java connectors run `./gradlew :airbyte-integrations:connectors:<name>:integrationTest`.
- [ ] Code reviews completed
- [ ] Documentation updated 
    - [ ] Connector's `README.md`
    - [ ] `docs/SUMMARY.md`
    - [ ] `docs/integrations/<source or destination>/<name>.md` including changelog. See changelog [example](https://docs.airbyte.io/integrations/sources/stripe#changelog)
    - [ ] `docs/integrations/README.md`
    - [ ] `airbyte-integrations/builds.md`
- [ ] PR name follows [PR naming conventions](https://docs.airbyte.io/contributing-to-airbyte/updating-documentation#issues-and-pull-requests)
- [ ] Connector added to connector index like described [here](https://docs.airbyte.io/connector-development#publishing-a-connector)
   
#### Airbyter

If this is a community PR, the Airbyte engineer reviewing this PR is responsible for the below items. 
   
- [ ] Create a non-forked branch based on this PR and test the below items on it
- [ ] Build is successful
- [ ] Credentials added to Github CI. [Instructions](https://docs.airbyte.io/connector-development#using-credentials-in-ci). 
- [ ] [`/test connector=connectors/<name>` command](https://docs.airbyte.io/connector-development#updating-an-existing-connector) is passing. 
- [ ] New Connector version released on Dockerhub by running the `/publish` command described [here](https://docs.airbyte.io/connector-development#updating-an-existing-connector)
   
</p>
</details>


<details><summary> <strong> Updating a connector </strong></summary>
<p>
   
#### Community member or Airbyter
   
- [ ] Grant edit access to maintainers ([instructions](https://docs.github.com/en/github/collaborating-with-pull-requests/working-with-forks/allowing-changes-to-a-pull-request-branch-created-from-a-fork#enabling-repository-maintainer-permissions-on-existing-pull-requests))
- [ ] Secrets in the connector's spec are annotated with `airbyte_secret` 
- [ ] Unit & integration tests added and passing. Community members, please provide proof of success locally e.g: screenshot or copy-paste unit, integration, and acceptance test output. To run acceptance tests for a Python connector, follow instructions in the README. For java connectors run `./gradlew :airbyte-integrations:connectors:<name>:integrationTest`.
- [ ] Code reviews completed
- [ ] Documentation updated 
    - [ ] Connector's `README.md`
    - [ ] Changelog updated in `docs/integrations/<source or destination>/<name>.md` including changelog. See changelog [example](https://docs.airbyte.io/integrations/sources/stripe#changelog)
- [ ] PR name follows [PR naming conventions](https://docs.airbyte.io/contributing-to-airbyte/updating-documentation#issues-and-pull-requests)
- [ ] Connector version bumped like described [here](https://docs.airbyte.io/connector-development#publishing-a-connector)
   
#### Airbyter

If this is a community PR, the Airbyte engineer reviewing this PR is responsible for the below items. 
   
- [ ] Create a non-forked branch based on this PR and test the below items on it
- [ ] Build is successful
- [ ] Credentials added to Github CI. [Instructions](https://docs.airbyte.io/connector-development#using-credentials-in-ci). 
- [ ] [`/test connector=connectors/<name>` command](https://docs.airbyte.io/connector-development#updating-an-existing-connector) is passing. 
- [ ] New Connector version released on Dockerhub by running the `/publish` command described [here](https://docs.airbyte.io/connector-development#updating-an-existing-connector)

</p>
</details>

<details><summary> <strong> Connector Generator </strong> </summary>
<p>
   
- [ ] Issue acceptance criteria met
- [ ] PR name follows [PR naming conventions](https://docs.airbyte.io/contributing-to-airbyte/updating-documentation#issues-and-pull-requests)
- [ ] If adding a new generator, add it to the [list of scaffold modules being tested](https://github.com/airbytehq/airbyte/blob/master/airbyte-integrations/connector-templates/generator/build.gradle#L41)
- [ ] The generator test modules (all connectors with `-scaffold` in their name) have been updated with the latest scaffold by running `./gradlew :airbyte-integrations:connector-templates:generator:testScaffoldTemplates` then checking in your changes
- [ ] Documentation which references the generator is updated as needed.
</p>
</details>
