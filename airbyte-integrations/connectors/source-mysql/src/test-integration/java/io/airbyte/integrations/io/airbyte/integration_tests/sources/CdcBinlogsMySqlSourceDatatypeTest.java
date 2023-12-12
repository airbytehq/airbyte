/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.io.airbyte.integration_tests.sources;

import static io.airbyte.integrations.io.airbyte.integration_tests.sources.utils.TestConstants.INITIAL_CDC_WAITING_SECONDS;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import com.google.common.collect.Iterables;
import io.airbyte.cdk.db.Database;
import io.airbyte.cdk.db.factory.DSLContextFactory;
import io.airbyte.cdk.db.factory.DatabaseDriver;
import io.airbyte.cdk.db.jdbc.JdbcUtils;
import io.airbyte.cdk.integrations.standardtest.source.TestDataHolder;
import io.airbyte.cdk.integrations.standardtest.source.TestDestinationEnv;
import io.airbyte.cdk.integrations.util.HostPortResolver;
import io.airbyte.commons.features.EnvVariableFeatureFlags;
import io.airbyte.commons.json.Jsons;
import io.airbyte.protocol.models.JsonSchemaType;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteStateMessage;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import java.util.List;
import org.jooq.DSLContext;
import org.jooq.SQLDialect;
import org.junit.jupiter.api.extension.ExtendWith;
import org.testcontainers.containers.MySQLContainer;
import uk.org.webcompere.systemstubs.environment.EnvironmentVariables;
import uk.org.webcompere.systemstubs.jupiter.SystemStub;
import uk.org.webcompere.systemstubs.jupiter.SystemStubsExtension;

@ExtendWith(SystemStubsExtension.class)
public class CdcBinlogsMySqlSourceDatatypeTest extends AbstractMySqlSourceDatatypeTest {

  @SystemStub
  private EnvironmentVariables environmentVariables;

  private DSLContext dslContext;
  private JsonNode stateAfterFirstSync;

  @Override
  protected void tearDown(final TestDestinationEnv testEnv) {
    dslContext.close();
    container.close();
  }

  @Override
  protected List<AirbyteMessage> runRead(final ConfiguredAirbyteCatalog configuredCatalog) throws Exception {
    if (stateAfterFirstSync == null) {
      throw new RuntimeException("stateAfterFirstSync is null");
    }
    return super.runRead(configuredCatalog, stateAfterFirstSync);
  }

  @Override
  protected void postSetup() throws Exception {
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
    final List<AirbyteStateMessage> stateAfterFirstBatch = extractStateMessages(allMessages);
    stateAfterFirstSync = Jsons.jsonNode(List.of(Iterables.getLast(stateAfterFirstBatch)));
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
    environmentVariables.set(EnvVariableFeatureFlags.USE_STREAM_CAPABLE_STATE, "true");
    final JsonNode replicationMethod = Jsons.jsonNode(ImmutableMap.builder()
        .put("method", "CDC")
        .put("initial_waiting_seconds", INITIAL_CDC_WAITING_SECONDS)
        .build());
    config = Jsons.jsonNode(ImmutableMap.builder()
        .put(JdbcUtils.HOST_KEY, HostPortResolver.resolveHost(container))
        .put(JdbcUtils.PORT_KEY, HostPortResolver.resolvePort(container))
        .put(JdbcUtils.DATABASE_KEY, container.getDatabaseName())
        .put(JdbcUtils.USERNAME_KEY, container.getUsername())
        .put(JdbcUtils.PASSWORD_KEY, container.getPassword())
        .put("replication_method", replicationMethod)
        .put("is_test", true)
        .build());

    dslContext = DSLContextFactory.create(
        config.get(JdbcUtils.USERNAME_KEY).asText(),
        config.get(JdbcUtils.PASSWORD_KEY).asText(),
        DatabaseDriver.MYSQL.getDriverClassName(),
        String.format(DatabaseDriver.MYSQL.getUrlFormatString(),
            container.getHost(),
            container.getFirstMappedPort(),
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

  @Override
  protected void addDecimalValuesTest() {
    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("decimal")
            .airbyteType(JsonSchemaType.NUMBER)
            .fullSourceDataType("decimal(19,2)")
            .addInsertValues("1700000.01", "'123'")
            .addExpectedValues("1700000.01", "123.00")
            .build());
  }

}
