/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mysql;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import com.google.common.collect.Lists;
import io.airbyte.cdk.db.Database;
import io.airbyte.cdk.db.factory.DSLContextFactory;
import io.airbyte.cdk.db.factory.DataSourceFactory;
import io.airbyte.cdk.db.factory.DatabaseDriver;
import io.airbyte.cdk.db.jdbc.DefaultJdbcDatabase;
import io.airbyte.cdk.db.jdbc.JdbcDatabase;
import io.airbyte.cdk.db.jdbc.JdbcUtils;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.string.Strings;
import io.airbyte.integrations.source.mysql.cdc.MySqlDebeziumStateUtil;
import io.airbyte.integrations.source.mysql.cdc.MySqlDebeziumStateUtil.MysqlDebeziumStateAttributes;
import io.airbyte.protocol.models.Field;
import io.airbyte.protocol.models.JsonSchemaType;
import io.airbyte.protocol.models.v0.AirbyteCatalog;
import io.airbyte.protocol.models.v0.CatalogHelpers;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.SyncMode;
import java.sql.SQLException;
import java.time.Instant;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.Properties;
import org.jooq.SQLDialect;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;
import org.testcontainers.containers.MySQLContainer;

public class MysqlDebeziumStateUtilTest {

  private static final String DB_NAME = Strings.addRandomSuffix("db", "_", 10).toLowerCase();
  private static final String TABLE_NAME = Strings.addRandomSuffix("table", "_", 10).toLowerCase();
  private static final Properties MYSQL_PROPERTIES = new Properties();
  private static final String DB_CREATE_QUERY = "CREATE DATABASE " + DB_NAME;
  private static final String TABLE_CREATE_QUERY = "CREATE TABLE " + DB_NAME + "." + TABLE_NAME + " (id INTEGER, name VARCHAR(200), PRIMARY KEY(id))";
  private static final AirbyteCatalog CATALOG = new AirbyteCatalog().withStreams(List.of(
      CatalogHelpers.createAirbyteStream(
          TABLE_NAME,
          DB_NAME,
          Field.of("id", JsonSchemaType.INTEGER),
          Field.of("string", JsonSchemaType.STRING))
          .withSupportedSyncModes(Lists.newArrayList(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL))
          .withSourceDefinedPrimaryKey(List.of(List.of("id")))));
  protected static final ConfiguredAirbyteCatalog CONFIGURED_CATALOG = CatalogHelpers.toDefaultConfiguredCatalog(CATALOG);

  static {
    CONFIGURED_CATALOG.getStreams().forEach(s -> s.setSyncMode(SyncMode.INCREMENTAL));
    MYSQL_PROPERTIES.setProperty("connector.class", "io.debezium.connector.mysql.MySqlConnector");
    MYSQL_PROPERTIES.setProperty("database.server.id", "5000");
  }

  @Test
  public void debeziumInitialStateConstructTest() throws SQLException {
    try (final MySQLContainer<?> container = new MySQLContainer<>("mysql:8.0")) {
      container.start();
      initDB(container);
      final JdbcDatabase database = getJdbcDatabase(container);
      final MySqlDebeziumStateUtil mySqlDebeziumStateUtil = new MySqlDebeziumStateUtil();
      final JsonNode debeziumState = mySqlDebeziumStateUtil.constructInitialDebeziumState(MYSQL_PROPERTIES, CONFIGURED_CATALOG, database);
      Assertions.assertEquals(3, Jsons.object(debeziumState, Map.class).size());
      Assertions.assertTrue(debeziumState.has("is_compressed"));
      Assertions.assertFalse(debeziumState.get("is_compressed").asBoolean());
      Assertions.assertTrue(debeziumState.has("mysql_db_history"));
      Assertions.assertNotNull(debeziumState.get("mysql_db_history"));
      Assertions.assertTrue(debeziumState.has("mysql_cdc_offset"));
      final Map<String, String> mysqlCdcOffset = Jsons.object(debeziumState.get("mysql_cdc_offset"), Map.class);
      Assertions.assertEquals(1, mysqlCdcOffset.size());
      Assertions.assertTrue(mysqlCdcOffset.containsKey("[\"" + DB_NAME + "\",{\"server\":\"" + DB_NAME + "\"}]"));
      Assertions.assertNotNull(mysqlCdcOffset.get("[\"" + DB_NAME + "\",{\"server\":\"" + DB_NAME + "\"}]"));

      final Optional<MysqlDebeziumStateAttributes> parsedOffset = mySqlDebeziumStateUtil.savedOffset(MYSQL_PROPERTIES, CONFIGURED_CATALOG,
          debeziumState.get("mysql_cdc_offset"), database.getSourceConfig());
      Assertions.assertTrue(parsedOffset.isPresent());
      Assertions.assertNotNull(parsedOffset.get().binlogFilename());
      Assertions.assertTrue(parsedOffset.get().binlogPosition() > 0);
      Assertions.assertTrue(parsedOffset.get().gtidSet().isEmpty());
      container.stop();
    }
  }

  @Test
  public void formatTestWithGtid() {
    final MySqlDebeziumStateUtil mySqlDebeziumStateUtil = new MySqlDebeziumStateUtil();
    final JsonNode debeziumState = mySqlDebeziumStateUtil.format(new MysqlDebeziumStateAttributes("binlog.000002", 633,
        Optional.of("3E11FA47-71CA-11E1-9E33-C80AA9429562:1-5")), "db_fgnfxvllud", "db_fgnfxvllud", Instant.parse("2023-06-06T08:36:10.341842Z"));
    final Map<String, String> stateAsMap = Jsons.object(debeziumState, Map.class);
    Assertions.assertEquals(1, stateAsMap.size());
    Assertions.assertTrue(stateAsMap.containsKey("[\"db_fgnfxvllud\",{\"server\":\"db_fgnfxvllud\"}]"));
    Assertions.assertEquals(
        "{\"transaction_id\":null,\"ts_sec\":1686040570,\"file\":\"binlog.000002\",\"pos\":633,\"gtids\":\"3E11FA47-71CA-11E1-9E33-C80AA9429562:1-5\"}",
        stateAsMap.get("[\"db_fgnfxvllud\",{\"server\":\"db_fgnfxvllud\"}]"));

    final JsonNode config = Jsons.jsonNode(ImmutableMap.builder()
        .put(JdbcUtils.HOST_KEY, "host")
        .put(JdbcUtils.PORT_KEY, "5432")
        .put(JdbcUtils.DATABASE_KEY, "db_fgnfxvllud")
        .put(JdbcUtils.USERNAME_KEY, "username")
        .put(JdbcUtils.PASSWORD_KEY, "password")
        .put(JdbcUtils.SSL_KEY, false)
        .build());

    final Optional<MysqlDebeziumStateAttributes> parsedOffset = mySqlDebeziumStateUtil.savedOffset(MYSQL_PROPERTIES, CONFIGURED_CATALOG,
        debeziumState, config);
    Assertions.assertTrue(parsedOffset.isPresent());
    final JsonNode stateGeneratedUsingParsedOffset =
        mySqlDebeziumStateUtil.format(parsedOffset.get(), "db_fgnfxvllud", "db_fgnfxvllud", Instant.parse("2023-06-06T08:36:10.341842Z"));
    Assertions.assertEquals(debeziumState, stateGeneratedUsingParsedOffset);
  }

  @Test
  public void formatTestWithoutGtid() {
    final MySqlDebeziumStateUtil mySqlDebeziumStateUtil = new MySqlDebeziumStateUtil();
    final JsonNode debeziumState = mySqlDebeziumStateUtil.format(new MysqlDebeziumStateAttributes("binlog.000002", 633,
        Optional.empty()), "db_fgnfxvllud", "db_fgnfxvllud", Instant.parse("2023-06-06T08:36:10.341842Z"));
    final Map<String, String> stateAsMap = Jsons.object(debeziumState, Map.class);
    Assertions.assertEquals(1, stateAsMap.size());
    Assertions.assertTrue(stateAsMap.containsKey("[\"db_fgnfxvllud\",{\"server\":\"db_fgnfxvllud\"}]"));
    Assertions.assertEquals("{\"transaction_id\":null,\"ts_sec\":1686040570,\"file\":\"binlog.000002\",\"pos\":633}",
        stateAsMap.get("[\"db_fgnfxvllud\",{\"server\":\"db_fgnfxvllud\"}]"));

    final JsonNode config = Jsons.jsonNode(ImmutableMap.builder()
        .put(JdbcUtils.HOST_KEY, "host")
        .put(JdbcUtils.PORT_KEY, "5432")
        .put(JdbcUtils.DATABASE_KEY, "db_fgnfxvllud")
        .put(JdbcUtils.USERNAME_KEY, "username")
        .put(JdbcUtils.PASSWORD_KEY, "password")
        .put(JdbcUtils.SSL_KEY, false)
        .build());

    final Optional<MysqlDebeziumStateAttributes> parsedOffset = mySqlDebeziumStateUtil.savedOffset(MYSQL_PROPERTIES, CONFIGURED_CATALOG,
        debeziumState, config);
    Assertions.assertTrue(parsedOffset.isPresent());
    final JsonNode stateGeneratedUsingParsedOffset =
        mySqlDebeziumStateUtil.format(parsedOffset.get(), "db_fgnfxvllud", "db_fgnfxvllud", Instant.parse("2023-06-06T08:36:10.341842Z"));
    Assertions.assertEquals(debeziumState, stateGeneratedUsingParsedOffset);
  }

  private JdbcDatabase getJdbcDatabase(final MySQLContainer<?> container) {
    final JdbcDatabase database = new DefaultJdbcDatabase(
        DataSourceFactory.create(
            "root",
            "test",
            DatabaseDriver.MYSQL.getDriverClassName(),
            String.format(DatabaseDriver.MYSQL.getUrlFormatString(),
                container.getHost(),
                container.getFirstMappedPort(),
                DB_NAME)));
    database.setSourceConfig(getSourceConfig(container));
    return database;
  }

  private void initDB(final MySQLContainer<?> container) throws SQLException {
    final Database db = new Database(DSLContextFactory.create(
        "root",
        "test",
        DatabaseDriver.MYSQL.getDriverClassName(),
        String.format("jdbc:mysql://%s:%s",
            container.getHost(),
            container.getFirstMappedPort()),
        SQLDialect.MYSQL));
    db.query(ctx -> ctx.execute(DB_CREATE_QUERY));
    db.query(ctx -> ctx.execute(TABLE_CREATE_QUERY));
  }

  private JsonNode getSourceConfig(final MySQLContainer<?> container) {
    final Map<String, Object> config = new HashMap<>();
    config.put(JdbcUtils.USERNAME_KEY, "root");
    config.put(JdbcUtils.PASSWORD_KEY, "test");
    config.put(JdbcUtils.HOST_KEY, container.getHost());
    config.put(JdbcUtils.PORT_KEY, container.getFirstMappedPort());
    config.put(JdbcUtils.DATABASE_KEY, DB_NAME);
    return Jsons.jsonNode(config);
  }

}
