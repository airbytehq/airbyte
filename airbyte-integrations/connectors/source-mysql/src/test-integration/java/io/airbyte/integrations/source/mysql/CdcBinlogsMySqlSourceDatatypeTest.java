/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mysql;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.Database;
import io.airbyte.db.factory.DSLContextFactory;
import io.airbyte.db.factory.DatabaseDriver;
import io.airbyte.db.jdbc.JdbcUtils;
import io.airbyte.integrations.standardtest.source.TestDataHolder;
import io.airbyte.integrations.standardtest.source.TestDestinationEnv;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteStateMessage;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.JsonSchemaType;
import java.util.List;
import org.jooq.DSLContext;
import org.jooq.SQLDialect;
import org.testcontainers.containers.MySQLContainer;

public class CdcBinlogsMySqlSourceDatatypeTest extends AbstractMySqlSourceDatatypeTest {

  private DSLContext dslContext;
  private JsonNode stateAfterFirstSync;

  @Override
  protected void tearDown(final TestDestinationEnv testEnv) {
    dslContext.close();
    container.close();
  }

  @Override
  protected List<AirbyteMessage> runRead(ConfiguredAirbyteCatalog configuredCatalog) throws Exception {
    if (stateAfterFirstSync == null) {
      throw new RuntimeException("stateAfterFirstSync is null");
    }
    return super.runRead(configuredCatalog, stateAfterFirstSync);
  }

  @Override
  protected void setupEnvironment(TestDestinationEnv environment) throws Exception {
    final Database database = setupDatabase();
    initTests();
    for (final TestDataHolder test : testDataHolders) {
      database.query(ctx -> {
        ctx.fetch(test.getCreateSqlQuery());
        return null;
      });
    }

    final ConfiguredAirbyteStream dummyTableWithData = createDummyTableWithData(database);
    final ConfiguredAirbyteCatalog catalog = getConfiguredCatalog();
    catalog.getStreams().add(dummyTableWithData);

    final List<AirbyteMessage> allMessages = super.runRead(catalog);
    if (allMessages.size() != 2) {
      throw new RuntimeException("First sync should only generate 2 records");
    }
    final List<AirbyteStateMessage> stateAfterFirstBatch = extractStateMessages(allMessages);
    if (stateAfterFirstBatch == null || stateAfterFirstBatch.isEmpty()) {
      throw new RuntimeException("stateAfterFirstBatch should not be null or empty");
    }
    stateAfterFirstSync = Jsons.jsonNode(stateAfterFirstBatch);
    if (stateAfterFirstSync == null) {
      throw new RuntimeException("stateAfterFirstSync should not be null");
    }
    for (final TestDataHolder test : testDataHolders) {
      database.query(ctx -> {
        test.getInsertSqlQueries().forEach(ctx::fetch);
        return null;
      });
    }
  }

  @Override
  protected Database setupDatabase() throws Exception {
    container = new MySQLContainer<>("mysql:8.0");
    container.start();

    config = Jsons.jsonNode(ImmutableMap.builder()
        .put(JdbcUtils.HOST_KEY, container.getHost())
        .put(JdbcUtils.PORT_KEY, container.getFirstMappedPort())
        .put(JdbcUtils.DATABASE_KEY, container.getDatabaseName())
        .put(JdbcUtils.USERNAME_KEY, container.getUsername())
        .put(JdbcUtils.PASSWORD_KEY, container.getPassword())
        .put("replication_method", MySqlSource.ReplicationMethod.CDC)
        .build());

    dslContext = DSLContextFactory.create(
        config.get(JdbcUtils.USERNAME_KEY).asText(),
        config.get(JdbcUtils.PASSWORD_KEY).asText(),
        DatabaseDriver.MYSQL.getDriverClassName(),
        String.format(DatabaseDriver.MYSQL.getUrlFormatString(),
            config.get(JdbcUtils.HOST_KEY).asText(),
            config.get(JdbcUtils.PORT_KEY).asInt(),
            config.get(JdbcUtils.DATABASE_KEY).asText()),
        SQLDialect.MYSQL);
    final Database database = new Database(dslContext);

    // It disable strict mode in the DB and allows to insert specific values.
    // For example, it's possible to insert date with zero values "2021-00-00"
    database.query(ctx -> ctx.fetch("SET @@sql_mode=''"));

    revokeAllPermissions();
    grantCorrectPermissions();

    return database;
  }

  private void revokeAllPermissions() {
    executeQuery("REVOKE ALL PRIVILEGES, GRANT OPTION FROM " + container.getUsername() + "@'%';");
  }

  private void grantCorrectPermissions() {
    executeQuery(
        "GRANT SELECT, RELOAD, SHOW DATABASES, REPLICATION SLAVE, REPLICATION CLIENT ON *.* TO "
            + container.getUsername() + "@'%';");
  }

  private void executeQuery(final String query) {
    try (final DSLContext dslContext = DSLContextFactory.create(
        "root",
        "test",
        DatabaseDriver.MYSQL.getDriverClassName(),
        String.format(DatabaseDriver.MYSQL.getUrlFormatString(),
            container.getHost(),
            container.getFirstMappedPort(),
            container.getDatabaseName()),
        SQLDialect.MYSQL)) {
      final Database database = new Database(dslContext);
      database.query(
          ctx -> ctx
              .execute(query));
    } catch (final Exception e) {
      throw new RuntimeException(e);
    }
  }

  @Override
  public boolean testCatalog() {
    return true;
  }

  @Override
  protected void addTimestampDataTypeTest() {
    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("timestamp")
            .airbyteType(JsonSchemaType.STRING_TIMESTAMP_WITH_TIMEZONE)
            .addInsertValues("null", "'2021-01-00'", "'2021-00-00'", "'0000-00-00'", "'2022-08-09T10:17:16.161342Z'")
            .addExpectedValues(null, "1970-01-01T00:00:00.000000Z", "1970-01-01T00:00:00.000000Z", "1970-01-01T00:00:00.000000Z",
                "2022-08-09T10:17:16.000000Z")
            .build());
  }

  @Override
  protected void addJsonDataTypeTest() {
    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("json")
            .airbyteType(JsonSchemaType.STRING)
            .addInsertValues("null", "'{\"a\":10,\"b\":15}'", "'{\"fóo\":\"bär\"}'", "'{\"春江潮水连海平\":\"海上明月共潮生\"}'")
            .addExpectedValues(null, "{\"a\":10,\"b\":15}", "{\"fóo\":\"bär\"}", "{\"春江潮水连海平\":\"海上明月共潮生\"}")
            .build());
  }

}
