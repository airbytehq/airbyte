/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.io.airbyte.integration_tests.sources;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.cdk.integrations.source.jdbc.test.JdbcSourceAcceptanceTest;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.source.redshift.RedshiftSource;
import io.airbyte.protocol.models.Field;
import io.airbyte.protocol.models.JsonSchemaType;
import io.airbyte.protocol.models.v0.AirbyteCatalog;
import io.airbyte.protocol.models.v0.CatalogHelpers;
import io.airbyte.protocol.models.v0.SyncMode;
import java.nio.file.Path;
import java.util.Collections;
import java.util.List;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;

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

  // The shared test tables declare updated_at as DATE, which Redshift discovers with a date format.
  @Override
  protected AirbyteCatalog getCatalog(final String defaultNamespace) {
    return new AirbyteCatalog().withStreams(List.of(
        CatalogHelpers.createAirbyteStream(
            TABLE_NAME,
            defaultNamespace,
            Field.of(COL_ID, JsonSchemaType.INTEGER),
            Field.of(COL_NAME, JsonSchemaType.STRING),
            Field.of(COL_UPDATED_AT, JsonSchemaType.STRING_DATE))
            .withSupportedSyncModes(List.of(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL))
            .withSourceDefinedPrimaryKey(List.of(List.of(COL_ID))),
        CatalogHelpers.createAirbyteStream(
            TABLE_NAME_WITHOUT_PK,
            defaultNamespace,
            Field.of(COL_ID, JsonSchemaType.INTEGER),
            Field.of(COL_NAME, JsonSchemaType.STRING),
            Field.of(COL_UPDATED_AT, JsonSchemaType.STRING_DATE))
            .withSupportedSyncModes(List.of(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL))
            .withSourceDefinedPrimaryKey(Collections.emptyList()),
        CatalogHelpers.createAirbyteStream(
            TABLE_NAME_COMPOSITE_PK,
            defaultNamespace,
            Field.of(COL_FIRST_NAME, JsonSchemaType.STRING),
            Field.of(COL_LAST_NAME, JsonSchemaType.STRING),
            Field.of(COL_UPDATED_AT, JsonSchemaType.STRING_DATE))
            .withSupportedSyncModes(List.of(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL))
            .withSourceDefinedPrimaryKey(
                List.of(List.of(COL_FIRST_NAME), List.of(COL_LAST_NAME)))));
  }

  @Test
  @Override
  protected void testCheckFailure() throws Exception {
    // no-op
  }

}
