/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.io.airbyte.integration_tests.sources;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.cdk.integrations.source.jdbc.test.JdbcSourceAcceptanceTest;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.source.redshift.RedshiftSource;
import java.nio.file.Path;
import org.junit.jupiter.api.BeforeAll;

// Run as part of integration tests, instead of unit tests, because there is no test container for
// Redshift.
class RedshiftJdbcSourceAcceptanceTest extends JdbcSourceAcceptanceTest<RedshiftSource, RedshiftTestDatabase> {

  private static JsonNode config;

  @BeforeAll
  static void init() {
    config = Jsons.deserialize(IOs.readFile(Path.of("secrets/config.json")));
    CREATE_TABLE_WITHOUT_CURSOR_TYPE_QUERY = "CREATE TABLE %s (%s GEOMETRY)";
    INSERT_TABLE_WITHOUT_CURSOR_TYPE_QUERY = "INSERT INTO %s VALUES(ST_Point(129.77099609375, 62.093299865722656))";
  }

  @Override
  protected RedshiftTestDatabase createTestDatabase() {
    final RedshiftTestDatabase testDatabase = new RedshiftTestDatabase(source().toDatabaseConfig(Jsons.clone(config))).initialized();
    try {
      for (final String schemaName : TEST_SCHEMAS) {
        testDatabase.with(DROP_SCHEMA_QUERY, schemaName);
      }
    } catch (final Exception ignore) {}
    return testDatabase;
  }

  @Override
  public boolean supportsSchemas() {
    return true;
  }

  @Override
  protected RedshiftSource source() {
    return new RedshiftSource();
  }

  @Override
  protected JsonNode config() {
    return Jsons.clone(config);
  }

}
