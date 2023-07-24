package io.airbyte.integrations.io.airbyte.integration_tests.sources;

/**
 * This is testing xmin sync with an older version of PostgreSQL which reclassifies ctid syncs back to xmin
 * Initial load of table is done with xmin.
 */
public class XminPostgresSourceWithOldPostgresAcceptanceTest extends XminPostgresSourceAcceptanceTest{

  @Override
  protected String getDockerImageName() {
    return "postgres:9-alpine";
  }
}
