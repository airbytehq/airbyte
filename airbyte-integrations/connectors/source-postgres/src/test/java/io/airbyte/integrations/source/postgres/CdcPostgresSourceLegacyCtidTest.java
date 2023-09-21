package io.airbyte.integrations.source.postgres;

public class CdcPostgresSourceLegacyCtidTest extends CdcPostgresSourceTest {

  @Override
  protected String getServerImageName() {
    return "debezium/postgres:13-alpine";
  }
}
