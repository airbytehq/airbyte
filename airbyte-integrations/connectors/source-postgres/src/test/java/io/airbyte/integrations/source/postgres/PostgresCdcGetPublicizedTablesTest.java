/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres;

import static org.junit.jupiter.api.Assertions.assertEquals;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.cdk.db.jdbc.DefaultJdbcDatabase;
import io.airbyte.cdk.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.source.postgres.PostgresTestDatabase.BaseImage;
import io.airbyte.integrations.source.postgres.PostgresTestDatabase.ContainerModifier;
import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair;
import java.sql.SQLException;
import java.util.Set;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

/**
 * This class tests the {@link PostgresCatalogHelper#getPublicizedTables} method.
 */
class PostgresCdcGetPublicizedTablesTest {

  private static final String SCHEMA_NAME = "public";
  private PostgresTestDatabase testdb;

  @BeforeEach
  void setup() {
    testdb = PostgresTestDatabase.in(BaseImage.POSTGRES_16, ContainerModifier.CONF)
        .with("create table table_1 (id serial primary key, text_column text);")
        .with("create table table_2 (id serial primary key, text_column text);")
        .with("create table table_irrelevant (id serial primary key, text_column text);")
        .withReplicationSlot();
    // create a publication including table_1 and table_2, but not table_irrelevant
    testdb = testdb
        .with("CREATE PUBLICATION %s FOR TABLE table_1, table_2;", testdb.getPublicationName())
        .onClose("DROP PUBLICATION %s CASCADE", testdb.getPublicationName());
  }

  @AfterEach
  void tearDown() {
    testdb.close();
  }

  private JsonNode getConfig() {
    return testdb.testConfigBuilder().withSchemas(SCHEMA_NAME).withoutSsl().with("is_test", true).build();
  }

  @Test
  public void testGetPublicizedTables() throws SQLException {
    final JdbcDatabase database = new DefaultJdbcDatabase(testdb.getDslContext().diagnosticsDataSource());
    // when source config does not exist
    assertEquals(0, PostgresCatalogHelper.getPublicizedTables(database).size());

    // when config is not cdc
    database.setSourceConfig(getConfig());
    assertEquals(0, PostgresCatalogHelper.getPublicizedTables(database).size());

    // when config is cdc
    final JsonNode cdcConfig =
        testdb.testConfigBuilder().withSchemas(SCHEMA_NAME).withoutSsl().withCdcReplication().build();
    database.setSourceConfig(cdcConfig);
    final Set<AirbyteStreamNameNamespacePair> expectedTables = Set.of(
        new AirbyteStreamNameNamespacePair("table_1", SCHEMA_NAME),
        new AirbyteStreamNameNamespacePair("table_2", SCHEMA_NAME));
    // table_irrelevant is not included because it is not part of the publication
    assertEquals(expectedTables, PostgresCatalogHelper.getPublicizedTables(database));
  }

}
