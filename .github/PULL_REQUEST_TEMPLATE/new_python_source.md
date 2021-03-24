## Contributor Checklist
Thanks for contributing to Airbyte! Please complete the following items in order so we can review your PR.
- [ ] Followed all the instructions in the locally generated checklist and your connector is functional & ready for review
- [ ] Ran the standard test suite locally via `./gradlew :airbyte-integrations:connectors:source-<your_source_name>:standardSourceTestPython` and pasted the summarized output as a comment in this PR
- [ ] Added the connector to the [connector health page](https://docs.airbyte.io/integrations/connector-health)

## Reviewer Pre-merge Checklist 
- [ ] Finished iterating with the PR author on the code*
- [ ] Created a branch off master to merge this PR into*
- [ ] Inject the credentials in CI via `./tools/integrations/ci_credentials.sh` and `.github/workflows/test-command.yml`*
- [ ] Added the credentials for this integration to Github secrets 
- [ ] Run standard tests on this branch by commenting `/test connector=<name>`*
- [ ] Add entry in `airbyte-config/init/src/main/resources/seed/source_definitions.yaml` to use the new source in Airbyte core
- [ ] Deployed the connector to Dockerhub via `./tools/integrations/manage.sh publish airbyte-integrations/connectors/source-<name>`

## Documentation
- [ ] Add docs in `docs/integrations/sources/` folder in line with the documentation template found in `docs/contributing-to-airbyte/templates/integration-documentation-template.md`.
- [ ] Add link to create docs file to `docs/SUMMARY.md`
- [ ] Include a link to the documentation in the `README.md`
