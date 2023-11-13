/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres;

import static org.junit.jupiter.api.Assertions.assertEquals;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.cdk.db.jdbc.DefaultJdbcDatabase;
import io.airbyte.cdk.db.jdbc.JdbcDatabase;
import io.airbyte.cdk.db.jdbc.JdbcUtils;
import io.airbyte.cdk.testutils.PostgresTestDatabase;
import io.airbyte.commons.json.Jsons;
import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair;
import java.sql.SQLException;
import java.util.List;
import java.util.Set;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

/**
 * This class tests the {@link PostgresCatalogHelper#getPublicizedTables} method.
 */
class PostgresCdcGetPublicizedTablesTest {

  private static final String SCHEMA_NAME = "public";
  protected static final int INITIAL_WAITING_SECONDS = 30;
  private String publication;
  private String replicationSlot;
  private PostgresTestDatabase testdb;

  @BeforeEach
  void setup() throws Exception {
    testdb = PostgresTestDatabase.make("postgres:16-bullseye", "withConf");
    replicationSlot = testdb.withSuffix("replication_slot");
    publication = testdb.withSuffix("publication");
    testdb.database.query(ctx -> {
      ctx.execute("create table table_1 (id serial primary key, text_column text);");
      ctx.execute("create table table_2 (id serial primary key, text_column text);");
      ctx.execute("create table table_irrelevant (id serial primary key, text_column text);");
      ctx.execute("SELECT pg_create_logical_replication_slot('" + replicationSlot + "', 'pgoutput');");
      // create a publication including table_1 and table_2, but not table_irrelevant
      ctx.execute("CREATE PUBLICATION " + publication + " FOR TABLE table_1, table_2;");
      return null;
    });
  }

  @AfterEach
  void tearDown() throws SQLException {
    testdb.database.query(ctx -> {
      ctx.execute("DROP PUBLICATION " + publication + ";");
      ctx.execute("SELECT pg_drop_replication_slot('" + replicationSlot + "');");
      return null;
    });
    testdb.close();
  }

  private JsonNode getConfig() {
    return Jsons.jsonNode(ImmutableMap.builder()
        .put(JdbcUtils.HOST_KEY, testdb.container.getHost())
        .put(JdbcUtils.PORT_KEY, testdb.container.getFirstMappedPort())
        .put(JdbcUtils.DATABASE_KEY, testdb.dbName)
        .put(JdbcUtils.SCHEMAS_KEY, List.of(SCHEMA_NAME))
        .put(JdbcUtils.USERNAME_KEY, testdb.userName)
        .put(JdbcUtils.PASSWORD_KEY, testdb.password)
        .put(JdbcUtils.SSL_KEY, false)
        .put("is_test", true)
        .build());
  }

  @Test
  public void testGetPublicizedTables() throws SQLException {
    final JdbcDatabase database = new DefaultJdbcDatabase(testdb.dslContext.diagnosticsDataSource());
    // when source config does not exist
    assertEquals(0, PostgresCatalogHelper.getPublicizedTables(database).size());

    // when config is not cdc
    database.setSourceConfig(getConfig());
    assertEquals(0, PostgresCatalogHelper.getPublicizedTables(database).size());

    // when config is cdc
    final ObjectNode cdcConfig = ((ObjectNode) getConfig());
    cdcConfig.set("replication_method", Jsons.jsonNode(ImmutableMap.of(
        "replication_slot", replicationSlot,
        "initial_waiting_seconds", INITIAL_WAITING_SECONDS,
        "publication", publication)));
    database.setSourceConfig(cdcConfig);
    final Set<AirbyteStreamNameNamespacePair> expectedTables = Set.of(
        new AirbyteStreamNameNamespacePair("table_1", SCHEMA_NAME),
        new AirbyteStreamNameNamespacePair("table_2", SCHEMA_NAME));
    // table_irrelevant is not included because it is not part of the publication
    assertEquals(expectedTables, PostgresCatalogHelper.getPublicizedTables(database));
  }

}
