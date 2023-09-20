package io.airbyte.integrations.io.airbyte.integration_tests.sources;

public class CdcPostgresSourceAcceptanceLegacyCtidTest extends CdcPostgresSourceAcceptanceTest{
  @Override
  protected String getServerImageName() {
    return "postgres:13-alpine";
  }
}
