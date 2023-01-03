/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres;

import static org.junit.jupiter.api.Assertions.assertEquals;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.string.Strings;
import io.airbyte.db.Database;
import io.airbyte.db.factory.DSLContextFactory;
import io.airbyte.db.factory.DatabaseDriver;
import io.airbyte.db.jdbc.DefaultJdbcDatabase;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.db.jdbc.JdbcUtils;
import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair;
import io.airbyte.test.utils.PostgreSQLContainerHelper;
import java.sql.SQLException;
import java.util.List;
import java.util.Set;
import org.jooq.DSLContext;
import org.jooq.SQLDialect;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.testcontainers.containers.PostgreSQLContainer;
import org.testcontainers.utility.DockerImageName;
import org.testcontainers.utility.MountableFile;

/**
 * This class tests the {@link PostgresCdcCatalogHelper#getPublicizedTables} method.
 */
class PostgresCdcGetPublicizedTablesTest {

  private static final String SCHEMA_NAME = "public";
  private static final String PUBLICATION = "publication_test_12";
  private static final String REPLICATION_SLOT = "replication_slot_test_12";
  protected static final int INITIAL_WAITING_SECONDS = 5;
  private static PostgreSQLContainer<?> container;
  private JsonNode config;

  @BeforeAll
  static void init() {
    final DockerImageName myImage = DockerImageName.parse("debezium/postgres:13-alpine").asCompatibleSubstituteFor("postgres");
    container = new PostgreSQLContainer<>(myImage)
        .withCopyFileToContainer(MountableFile.forClasspathResource("postgresql.conf"), "/etc/postgresql/postgresql.conf")
        .withCommand("postgres -c config_file=/etc/postgresql/postgresql.conf");
    container.start();
  }

  @AfterAll
  static void cleanUp() {
    container.close();
  }

  @BeforeEach
  void setup() throws Exception {
    final String dbName = Strings.addRandomSuffix("db", "_", 10).toLowerCase();
    final String initScriptName = "init_" + dbName.concat(".sql");
    final String tmpFilePath = IOs.writeFileToRandomTmpDir(initScriptName, "CREATE DATABASE " + dbName + ";");
    PostgreSQLContainerHelper.runSqlScript(MountableFile.forHostPath(tmpFilePath), container);

    this.config = getConfig(container, dbName);

    try (final DSLContext dslContext = getDslContext(config)) {
      final Database database = getDatabase(dslContext);
      database.query(ctx -> {
        ctx.execute("create table table_1 (id serial primary key, text_column text);");
        ctx.execute("create table table_2 (id serial primary key, text_column text);");
        ctx.execute("create table table_irrelevant (id serial primary key, text_column text);");
        ctx.execute("SELECT pg_create_logical_replication_slot('" + REPLICATION_SLOT + "', 'pgoutput');");
        // create a publication including table_1 and table_2, but not table_irrelevant
        ctx.execute("CREATE PUBLICATION " + PUBLICATION + " FOR TABLE table_1, table_2;");
        return null;
      });
    }
  }

  private JsonNode getConfig(final PostgreSQLContainer<?> psqlDb, final String dbName) {
    return Jsons.jsonNode(ImmutableMap.builder()
        .put(JdbcUtils.HOST_KEY, psqlDb.getHost())
        .put(JdbcUtils.PORT_KEY, psqlDb.getFirstMappedPort())
        .put(JdbcUtils.DATABASE_KEY, dbName)
        .put(JdbcUtils.SCHEMAS_KEY, List.of(SCHEMA_NAME))
        .put(JdbcUtils.USERNAME_KEY, psqlDb.getUsername())
        .put(JdbcUtils.PASSWORD_KEY, psqlDb.getPassword())
        .put(JdbcUtils.SSL_KEY, false)
        .put("is_test", true)
        .build());
  }

  private static DSLContext getDslContext(final JsonNode config) {
    return DSLContextFactory.create(
        config.get(JdbcUtils.USERNAME_KEY).asText(),
        config.get(JdbcUtils.PASSWORD_KEY).asText(),
        DatabaseDriver.POSTGRESQL.getDriverClassName(),
        String.format(DatabaseDriver.POSTGRESQL.getUrlFormatString(),
            config.get(JdbcUtils.HOST_KEY).asText(),
            config.get(JdbcUtils.PORT_KEY).asInt(),
            config.get(JdbcUtils.DATABASE_KEY).asText()),
        SQLDialect.POSTGRES);
  }

  private static Database getDatabase(final DSLContext dslContext) {
    return new Database(dslContext);
  }

  @Test
  public void testGetPublicizedTables() {
    try (final DSLContext dslContext = getDslContext(config)) {
      final JdbcDatabase database = new DefaultJdbcDatabase(dslContext.diagnosticsDataSource());
      // when source config does not exist
      assertEquals(0, PostgresCdcCatalogHelper.getPublicizedTables(database).size());

      // when config is not cdc
      database.setSourceConfig(config);
      assertEquals(0, PostgresCdcCatalogHelper.getPublicizedTables(database).size());

      // when config is cdc
      ((ObjectNode) config).set("replication_method", Jsons.jsonNode(ImmutableMap.of(
          "replication_slot", REPLICATION_SLOT,
          "initial_waiting_seconds", INITIAL_WAITING_SECONDS,
          "publication", PUBLICATION)));
      database.setSourceConfig(config);
      final Set<AirbyteStreamNameNamespacePair> expectedTables = Set.of(
          new AirbyteStreamNameNamespacePair("table_1", SCHEMA_NAME),
          new AirbyteStreamNameNamespacePair("table_2", SCHEMA_NAME));
      // table_irrelevant is not included because it is not part of the publication
      assertEquals(expectedTables, PostgresCdcCatalogHelper.getPublicizedTables(database));
    } catch (final SQLException e) {
      throw new RuntimeException(e);
    }
  }

}
