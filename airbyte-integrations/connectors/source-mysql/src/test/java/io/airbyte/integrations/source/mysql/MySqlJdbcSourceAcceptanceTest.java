/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mysql;

import static org.assertj.core.api.AssertionsForClassTypes.assertThat;
import static org.assertj.core.api.AssertionsForClassTypes.catchThrowable;
import static org.junit.jupiter.api.Assertions.assertEquals;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.collect.ImmutableMap;
import com.mysql.cj.MysqlType;
import io.airbyte.commons.exceptions.ConfigErrorException;
import io.airbyte.commons.features.EnvVariableFeatureFlags;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.commons.string.Strings;
import io.airbyte.db.Database;
import io.airbyte.db.factory.DSLContextFactory;
import io.airbyte.db.factory.DatabaseDriver;
import io.airbyte.db.jdbc.JdbcUtils;
import io.airbyte.integrations.source.jdbc.AbstractJdbcSource;
import io.airbyte.integrations.source.jdbc.test.JdbcSourceAcceptanceTest;
import io.airbyte.integrations.source.relationaldb.models.DbStreamState;
import io.airbyte.protocol.models.AirbyteCatalog;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteMessage.Type;
import io.airbyte.protocol.models.AirbyteRecordMessage;
import io.airbyte.protocol.models.CatalogHelpers;
import io.airbyte.protocol.models.ConnectorSpecification;
import io.airbyte.protocol.models.Field;
import io.airbyte.protocol.models.JsonSchemaType;
import io.airbyte.protocol.models.SyncMode;
import java.sql.Connection;
import java.sql.DriverManager;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Map;
import java.util.concurrent.Callable;
import org.jooq.DSLContext;
import org.jooq.SQLDialect;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.testcontainers.containers.MySQLContainer;

class MySqlJdbcSourceAcceptanceTest extends JdbcSourceAcceptanceTest {

  protected static final String USERNAME_WITHOUT_PERMISSION = "new_user";
  protected static final String PASSWORD_WITHOUT_PERMISSION = "new_password";
  protected static final String TEST_USER = "test";
  protected static final Callable<String> TEST_PASSWORD = () -> "test";
  protected static MySQLContainer<?> container;

  protected Database database;
  protected DSLContext dslContext;

  @BeforeAll
  static void init() throws Exception {
    setEnv(EnvVariableFeatureFlags.USE_STREAM_CAPABLE_STATE, "true");
    container = new MySQLContainer<>("mysql:8.0")
        .withUsername(TEST_USER)
        .withPassword(TEST_PASSWORD.call())
        .withEnv("MYSQL_ROOT_HOST", "%")
        .withEnv("MYSQL_ROOT_PASSWORD", TEST_PASSWORD.call());
    container.start();
    final Connection connection = DriverManager.getConnection(container.getJdbcUrl(), "root", TEST_PASSWORD.call());
    connection.createStatement().execute("GRANT ALL PRIVILEGES ON *.* TO '" + TEST_USER + "'@'%';\n");
  }

  @BeforeEach
  public void setup() throws Exception {
    config = Jsons.jsonNode(ImmutableMap.builder()
        .put(JdbcUtils.HOST_KEY, container.getHost())
        .put(JdbcUtils.PORT_KEY, container.getFirstMappedPort())
        .put(JdbcUtils.DATABASE_KEY, Strings.addRandomSuffix("db", "_", 10))
        .put(JdbcUtils.USERNAME_KEY, TEST_USER)
        .put(JdbcUtils.PASSWORD_KEY, TEST_PASSWORD.call())
        .build());

    dslContext = DSLContextFactory.create(
        config.get(JdbcUtils.USERNAME_KEY).asText(),
        config.get(JdbcUtils.PASSWORD_KEY).asText(),
        DatabaseDriver.MYSQL.getDriverClassName(),
        String.format("jdbc:mysql://%s:%s",
            config.get(JdbcUtils.HOST_KEY).asText(),
            config.get(JdbcUtils.PORT_KEY).asText()),
        SQLDialect.MYSQL);
    database = new Database(dslContext);

    database.query(ctx -> {
      ctx.fetch("CREATE DATABASE " + config.get(JdbcUtils.DATABASE_KEY).asText());
      return null;
    });

    super.setup();
  }

  @AfterEach
  void tearDownMySql() throws Exception {
    dslContext.close();
    super.tearDown();
  }

  @AfterAll
  static void cleanUp() {
    container.close();
  }

  // MySql does not support schemas in the way most dbs do. Instead we namespace by db name.
  @Override
  public boolean supportsSchemas() {
    return false;
  }

  @Override
  public AbstractJdbcSource<MysqlType> getJdbcSource() {
    return new MySqlSource();
  }

  @Override
  public String getDriverClass() {
    return MySqlSource.DRIVER_CLASS;
  }

  @Override
  public JsonNode getConfig() {
    return Jsons.clone(config);
  }

  @Test
  void testSpec() throws Exception {
    final ConnectorSpecification actual = source.spec();
    final ConnectorSpecification expected = Jsons.deserialize(MoreResources.readResource("spec.json"), ConnectorSpecification.class);

    assertEquals(expected, actual);
  }

  /**
   * MySQL Error Codes:
   * <p>
   * https://dev.mysql.com/doc/connector-j/8.0/en/connector-j-reference-error-sqlstates.html
   * </p>
   *
   * @throws Exception
   */
  @Test
  void testCheckIncorrectPasswordFailure() throws Exception {
    ((ObjectNode) config).put(JdbcUtils.PASSWORD_KEY, "fake");
    final Throwable throwable = catchThrowable(() -> source.check(config));
    assertThat(throwable).isInstanceOf(ConfigErrorException.class);
    assertThat(((ConfigErrorException) throwable).getDisplayMessage()
        .contains("State code: 08001;"));
  }

  @Test
  public void testCheckIncorrectUsernameFailure() throws Exception {
    ((ObjectNode) config).put(JdbcUtils.USERNAME_KEY, "fake");
    final Throwable throwable = catchThrowable(() -> source.check(config));
    assertThat(throwable).isInstanceOf(ConfigErrorException.class);
  }

  @Test
  public void testCheckIncorrectHostFailure() throws Exception {
    ((ObjectNode) config).put(JdbcUtils.HOST_KEY, "localhost2");
    final Throwable throwable = catchThrowable(() -> source.check(config));
    assertThat(throwable).isInstanceOf(ConfigErrorException.class);
    assertThat(((ConfigErrorException) throwable).getDisplayMessage()
        .contains("State code: 08S01;"));
  }

  @Test
  public void testCheckIncorrectPortFailure() throws Exception {
    ((ObjectNode) config).put(JdbcUtils.PORT_KEY, "0000");
    final Throwable throwable = catchThrowable(() -> source.check(config));
    assertThat(throwable).isInstanceOf(ConfigErrorException.class);
    assertThat(((ConfigErrorException) throwable).getDisplayMessage()
        .contains("State code: 08S01;"));
  }

  @Test
  public void testCheckIncorrectDataBaseFailure() throws Exception {
    ((ObjectNode) config).put(JdbcUtils.DATABASE_KEY, "wrongdatabase");
    final Throwable throwable = catchThrowable(() -> source.check(config));
    assertThat(throwable).isInstanceOf(ConfigErrorException.class);
    assertThat(((ConfigErrorException) throwable).getDisplayMessage()
        .contains("State code: 42000; Error code: 1049;"));
  }

  @Test
  public void testUserHasNoPermissionToDataBase() throws Exception {
    final Connection connection = DriverManager.getConnection(container.getJdbcUrl(), "root", TEST_PASSWORD.call());
    connection.createStatement()
        .execute("create user '" + USERNAME_WITHOUT_PERMISSION + "'@'%' IDENTIFIED BY '" + PASSWORD_WITHOUT_PERMISSION + "';\n");
    ((ObjectNode) config).put(JdbcUtils.USERNAME_KEY, USERNAME_WITHOUT_PERMISSION);
    ((ObjectNode) config).put(JdbcUtils.PASSWORD_KEY, PASSWORD_WITHOUT_PERMISSION);
    final Throwable throwable = catchThrowable(() -> source.check(config));
    assertThat(throwable).isInstanceOf(ConfigErrorException.class);
    assertThat(((ConfigErrorException) throwable).getDisplayMessage()
        .contains("State code: 08001;"));
  }

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

  @Override
  protected void incrementalDateCheck() throws Exception {
    incrementalCursorCheck(
        COL_UPDATED_AT,
        "2005-10-18",
        "2006-10-19",
        List.of(getTestMessages().get(1), getTestMessages().get(2)));
  }

  @Override
  protected List<AirbyteMessage> getTestMessages() {
    return List.of(
        new AirbyteMessage().withType(Type.RECORD)
            .withRecord(new AirbyteRecordMessage().withStream(streamName).withNamespace(getDefaultNamespace())
                .withData(Jsons.jsonNode(Map
                    .of(COL_ID, ID_VALUE_1,
                        COL_NAME, "picard",
                        COL_UPDATED_AT, "2004-10-19")))),
        new AirbyteMessage().withType(Type.RECORD)
            .withRecord(new AirbyteRecordMessage().withStream(streamName).withNamespace(getDefaultNamespace())
                .withData(Jsons.jsonNode(Map
                    .of(COL_ID, ID_VALUE_2,
                        COL_NAME, "crusher",
                        COL_UPDATED_AT,
                        "2005-10-19")))),
        new AirbyteMessage().withType(Type.RECORD)
            .withRecord(new AirbyteRecordMessage().withStream(streamName).withNamespace(getDefaultNamespace())
                .withData(Jsons.jsonNode(Map
                    .of(COL_ID, ID_VALUE_3,
                        COL_NAME, "vash",
                        COL_UPDATED_AT, "2006-10-19")))));
  }

  @Override
  protected List<AirbyteMessage> getExpectedAirbyteMessagesSecondSync(final String namespace) {
    final List<AirbyteMessage> expectedMessages = new ArrayList<>();
    expectedMessages.add(new AirbyteMessage().withType(Type.RECORD)
        .withRecord(new AirbyteRecordMessage().withStream(streamName).withNamespace(namespace)
            .withData(Jsons.jsonNode(Map
                .of(COL_ID, ID_VALUE_4,
                    COL_NAME, "riker",
                    COL_UPDATED_AT, "2006-10-19")))));
    expectedMessages.add(new AirbyteMessage().withType(Type.RECORD)
        .withRecord(new AirbyteRecordMessage().withStream(streamName).withNamespace(namespace)
            .withData(Jsons.jsonNode(Map
                .of(COL_ID, ID_VALUE_5,
                    COL_NAME, "data",
                    COL_UPDATED_AT, "2006-10-19")))));
    final DbStreamState state = new DbStreamState()
        .withStreamName(streamName)
        .withStreamNamespace(namespace)
        .withCursorField(List.of(COL_ID))
        .withCursor("5")
        .withCursorRecordCount(1L);
    expectedMessages.addAll(createExpectedTestMessages(List.of(state)));
    return expectedMessages;
  }

  @Override
  protected boolean supportsPerStream() {
    return true;
  }

}
