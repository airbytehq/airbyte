# New python source checklist

- [ ] Define the specification by modifying `spec.json`.
- [ ] Implement your integration in `source.py` (and creating additional files as necessary).
- [ ] Ensure that all logging done through the `logger` object passed into each method.
- [ ] Update the `sample_files` directory with an example config and catalog (discover output).

Tests

- [ ] Create unit tests in `unit_tests` folder.
- [ ] Create integration tests in `integration_tests` folder.
- [ ] Implement each method in `integration_tests/standard_source_test.py` if necessary.
- [ ] Run `./gradlew :airbyte-integrations:connectors:source-{{dashCase name}}:standardSourceTestPython`

Add your source to the source definition registry.

- [ ] Create file `{{unique UUIDv4}}.json` in `airbyte-config/init/src/main/resources/seed/STANDARD_SOURCE_DEFINITION` add update it. 
Put the same UUID in `sourceDefinitionId` field. Follow the example of the other entries.
- [ ] Add entry in `airbyte-config/init/src/main/resources/seed/source_definitions.yaml`

Add docs

- [ ] Add docs in `docs/integrations/sources/` folder. 
- [ ] If API credentials are required to run the integration, please document how they can be obtained.
- [ ] Add link to create docs file to `docs/SUMMARY.md`
- [ ] Update `README.md` to document the usage of your integration.
- [ ] Include a link to the documentation in the `README.md`.

- [ ] From the `airbyte` project root, run `./gradlew build` to make sure your module builds within the rest of the monorepo.
