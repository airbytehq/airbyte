# airbyte-tests

This module contains two major test suites:
1. Acceptance Tests - These are feature-level tests that run as part of the build. They spin up Airbyte and test functionality by executing commands against the Airbyte Configuration API. It is possible to run them both on `docker-compose` and `kuberenetes`. We do both in the build. These tests are designed to verify that large features work in broad strokes. More detailed testing should happen in unit tests.
2. Auto Migration Acceptance Tests - These tests verify that it is possible to upgrade from older version of Airbyte (as far back as 0.17.0) all the way up to the current version.
