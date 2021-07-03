## What
*Describe what the change is solving*
*It helps to add screenshots if it affects the frontend.*

## How
*Describe the solution*

## Recommended reading order
1. `x.java`
2. `y.python`

## Pre-merge Checklist
Expand the checklist which is relevant for this PR. 

<details><summary> <strong> Connector checklist </strong> </summary>
<p>

- [ ] Issue acceptance criteria met
- [ ] PR name follows [PR naming conventions](https://docs.airbyte.io/contributing-to-airbyte/updating-documentation#issues-and-pull-requests)
- [ ] Secrets are annotated with `airbyte_secret` in the connector's spec
- [ ] Credentials added to Github CI if needed and not already present. [instructions for injecting secrets into CI](https://docs.airbyte.io/contributing-to-airbyte/building-new-connector#using-credentials-in-ci). 
- [ ] Unit & integration tests added as appropriate (and are passing)
    * Community members: please provide proof of this succeeding locally e.g: screenshot or copy-paste acceptance test output. To run acceptance tests for a Python connector, follow instructions in the README. For java connectors run `./gradlew :airbyte-integrations:connectors:<name>:integrationTest`.
- [ ] `/test connector=connectors/<name>` command as documented [here](https://docs.airbyte.io/contributing-to-airbyte/building-new-connector#updating-an-existing-connector) is passing. 
    * Community members can skip this, Airbyters will run this for you. 
- [ ] Code reviews completed
- [ ] Documentation updated 
    - [ ] `README.md`
    - [ ] `docs/SUMMARY.md` if it's a new connector
    - [ ] Created or updated reference docs in `docs/integrations/<source or destination>/<name>`.
    - [ ] Changelog in the appropriate page in `docs/integrations/...`. See changelog [example](https://docs.airbyte.io/integrations/sources/stripe#changelog)
    - [ ] `docs/integrations/README.md` contains a reference to the new connector
    - [ ] Build status added to [build page](https://github.com/airbytehq/airbyte/blob/master/airbyte-integrations/builds.md)
- [ ] Build is successful
- [ ] Connector version bumped like described [here](https://docs.airbyte.io/contributing-to-airbyte/building-new-connector#updating-a-connector)
- [ ] New Connector version released on Dockerhub by running the `/publish` command described [here](https://docs.airbyte.io/contributing-to-airbyte/building-new-connector#updating-a-connector)
- [ ] No major blockers
- [ ] PR merged into master branch
- [ ] Follow up tickets have been created
- [ ] Associated tickets have been closed & stakeholders notified
</p>
</details>

<details><summary> <strong> Connector Generator checklist </strong> </summary>
<p>
   
- [ ] Issue acceptance criteria met
- [ ] PR name follows [PR naming conventions](https://docs.airbyte.io/contributing-to-airbyte/updating-documentation#issues-and-pull-requests)
- [ ] If adding a new generator, add it to the [list of scaffold modules being tested](https://github.com/airbytehq/airbyte/blob/master/airbyte-integrations/connector-templates/generator/build.gradle#L41)
- [ ] The generator test modules (all connectors with `-scaffold` in their name) have been updated with the latest scaffold by running `./gradlew :airbyte-integrations:connector-templates:generator:testScaffoldTemplates` then checking in your changes
- [ ] Documentation which references the generator is updated as needed.
</p>
</details>
