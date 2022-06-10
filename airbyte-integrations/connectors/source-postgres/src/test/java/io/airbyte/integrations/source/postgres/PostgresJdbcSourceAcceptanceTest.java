/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres;

import static org.junit.jupiter.api.Assertions.assertEquals;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.collect.ImmutableList;
import com.google.common.collect.ImmutableMap;
import com.google.common.collect.Lists;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.commons.string.Strings;
import io.airbyte.db.factory.DataSourceFactory;
import io.airbyte.db.jdbc.JdbcSourceOperations;
import io.airbyte.db.jdbc.JdbcUtils;
import io.airbyte.db.jdbc.StreamingJdbcDatabase;
import io.airbyte.db.jdbc.streaming.AdaptiveStreamingQueryConfig;
import io.airbyte.integrations.source.jdbc.AbstractJdbcSource;
import io.airbyte.integrations.source.jdbc.test.JdbcSourceAcceptanceTest;
import io.airbyte.integrations.source.relationaldb.models.DbState;
import io.airbyte.integrations.source.relationaldb.models.DbStreamState;
import io.airbyte.protocol.models.*;
import io.airbyte.test.utils.PostgreSQLContainerHelper;
import java.sql.JDBCType;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.stream.Collectors;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.testcontainers.containers.PostgreSQLContainer;
import org.testcontainers.utility.MountableFile;

class PostgresJdbcSourceAcceptanceTest extends JdbcSourceAcceptanceTest {

  private static PostgreSQLContainer<?> PSQL_DB;
  public static String COL_WAKEUP = "wakeup";
  public static String COL_BIRTH = "birth";

  @BeforeAll
  static void init() {
    PSQL_DB = new PostgreSQLContainer<>("postgres:13-alpine");
    PSQL_DB.start();
  }

  @BeforeEach
  public void setup() throws Exception {
    final String dbName = Strings.addRandomSuffix("db", "_", 10).toLowerCase();
    COLUMN_CLAUSE_WITH_PK = "id INTEGER, name VARCHAR(200), updated_at DATE, wakeup TIMETZ, birth TIMESTAMPTZ";
    COLUMN_CLAUSE_WITHOUT_PK = "id INTEGER, name VARCHAR(200), updated_at DATE, wakeup TIMETZ, birth TIMESTAMPTZ";
    COLUMN_CLAUSE_WITH_COMPOSITE_PK = "first_name VARCHAR(200), last_name VARCHAR(200), updated_at DATE, wakeup TIMETZ, birth TIMESTAMPTZ";

    config = Jsons.jsonNode(ImmutableMap.builder()
        .put("host", PSQL_DB.getHost())
        .put("port", PSQL_DB.getFirstMappedPort())
        .put("database", dbName)
        .put("schemas", List.of(SCHEMA_NAME, SCHEMA_NAME2))
        .put("username", PSQL_DB.getUsername())
        .put("password", PSQL_DB.getPassword())
        .put("ssl", false)
        .build());

    final String initScriptName = "init_" + dbName.concat(".sql");
    final String tmpFilePath = IOs.writeFileToRandomTmpDir(initScriptName, "CREATE DATABASE " + dbName + ";");
    PostgreSQLContainerHelper.runSqlScript(MountableFile.forHostPath(tmpFilePath), PSQL_DB);

    source = getSource();
    final JsonNode jdbcConfig = getToDatabaseConfigFunction().apply(config);

    streamName = TABLE_NAME;

    dataSource = DataSourceFactory.create(
        jdbcConfig.get("username").asText(),
        jdbcConfig.has("password") ? jdbcConfig.get("password").asText() : null,
        getDriverClass(),
        jdbcConfig.get("jdbc_url").asText(),
        JdbcUtils.parseJdbcParameters(jdbcConfig, "connection_properties", getJdbcParameterDelimiter()));

    database = new StreamingJdbcDatabase(dataSource,
        JdbcUtils.getDefaultSourceOperations(),
        AdaptiveStreamingQueryConfig::new);

    createSchemas();

    database.execute(connection -> {

      connection.createStatement().execute(
          createTableQuery(getFullyQualifiedTableName(TABLE_NAME), COLUMN_CLAUSE_WITH_PK,
              primaryKeyClause(Collections.singletonList("id"))));
      connection.createStatement().execute(
          String.format(
              "INSERT INTO %s(id, name, updated_at, wakeup, birth) VALUES (1,'picard', '2004-10-19','10:10:10.123456-05:00','2004-10-19T17:23:54.123456Z')",
              getFullyQualifiedTableName(TABLE_NAME)));
      connection.createStatement().execute(
          String.format(
              "INSERT INTO %s(id, name, updated_at, wakeup, birth) VALUES (2, 'crusher', '2005-10-19','11:11:11.123456-05:00','2005-10-19T17:23:54.123456Z')",
              getFullyQualifiedTableName(TABLE_NAME)));
      connection.createStatement().execute(
          String.format(
              "INSERT INTO %s(id, name, updated_at, wakeup, birth) VALUES (3, 'vash', '2006-10-19','12:12:12.123456-05:00','2006-10-19T17:23:54.123456Z')",
              getFullyQualifiedTableName(TABLE_NAME)));

      connection.createStatement().execute(
          createTableQuery(getFullyQualifiedTableName(TABLE_NAME_WITHOUT_PK),
              COLUMN_CLAUSE_WITHOUT_PK, ""));
      connection.createStatement().execute(
          String.format(
              "INSERT INTO %s(id, name, updated_at, wakeup, birth) VALUES (1,'picard', '2004-10-19','12:12:12.123456-05:00','2004-10-19T17:23:54.123456Z')",
              getFullyQualifiedTableName(TABLE_NAME_WITHOUT_PK)));
      connection.createStatement().execute(
          String.format(
              "INSERT INTO %s(id, name, updated_at, wakeup, birth) VALUES (2, 'crusher', '2005-10-19','11:11:11.123456-05:00','2005-10-19T17:23:54.123456Z')",
              getFullyQualifiedTableName(TABLE_NAME_WITHOUT_PK)));
      connection.createStatement().execute(
          String.format(
              "INSERT INTO %s(id, name, updated_at, wakeup, birth) VALUES (3, 'vash', '2006-10-19','10:10:10.123456-05:00','2006-10-19T17:23:54.123456Z')",
              getFullyQualifiedTableName(TABLE_NAME_WITHOUT_PK)));

      connection.createStatement().execute(
          createTableQuery(getFullyQualifiedTableName(TABLE_NAME_COMPOSITE_PK),
              COLUMN_CLAUSE_WITH_COMPOSITE_PK,
              primaryKeyClause(ImmutableList.of("first_name", "last_name"))));
      connection.createStatement().execute(
          String.format(
              "INSERT INTO %s(first_name, last_name, updated_at, wakeup, birth) VALUES ('first' ,'picard', '2004-10-19','12:12:12.123456-05:00','2004-10-19T17:23:54.123456Z')",
              getFullyQualifiedTableName(TABLE_NAME_COMPOSITE_PK)));
      connection.createStatement().execute(
          String.format(
              "INSERT INTO %s(first_name, last_name, updated_at, wakeup, birth) VALUES ('second', 'crusher', '2005-10-19','11:11:11.123456-05:00','2005-10-19T17:23:54.123456Z')",
              getFullyQualifiedTableName(TABLE_NAME_COMPOSITE_PK)));
      connection.createStatement().execute(
          String.format(
              "INSERT INTO %s(first_name, last_name, updated_at, wakeup, birth) VALUES  ('third', 'vash', '2006-10-19','10:10:10.123456-05:00','2006-10-19T17:23:54.123456Z')",
              getFullyQualifiedTableName(TABLE_NAME_COMPOSITE_PK)));

    });

  }

  @Override
  protected List<AirbyteMessage> getAirbyteMessagesReadOneColumn() {
    return getTestMessages().stream()
        .map(Jsons::clone)
        .peek(m -> {
          ((ObjectNode) m.getRecord().getData()).remove(COL_NAME);
          ((ObjectNode) m.getRecord().getData()).remove(COL_UPDATED_AT);
          ((ObjectNode) m.getRecord().getData()).remove(COL_WAKEUP);
          ((ObjectNode) m.getRecord().getData()).remove(COL_BIRTH);
          ((ObjectNode) m.getRecord().getData()).replace(COL_ID,
              Jsons.jsonNode(m.getRecord().getData().get(COL_ID).asInt()));
        })
        .collect(Collectors.toList());
  }

  @Override
  protected ArrayList<AirbyteMessage> getAirbyteMessagesCheckCursorSpaceInColumnName(ConfiguredAirbyteStream streamWithSpaces) {
    final AirbyteMessage firstMessage = getTestMessages().get(0);
    firstMessage.getRecord().setStream(streamWithSpaces.getStream().getName());
    ((ObjectNode) firstMessage.getRecord().getData()).remove(COL_UPDATED_AT);
    ((ObjectNode) firstMessage.getRecord().getData()).remove(COL_WAKEUP);
    ((ObjectNode) firstMessage.getRecord().getData()).remove(COL_BIRTH);
    ((ObjectNode) firstMessage.getRecord().getData()).set(COL_LAST_NAME_WITH_SPACE,
        ((ObjectNode) firstMessage.getRecord().getData()).remove(COL_NAME));

    final AirbyteMessage secondMessage = getTestMessages().get(2);
    secondMessage.getRecord().setStream(streamWithSpaces.getStream().getName());
    ((ObjectNode) secondMessage.getRecord().getData()).remove(COL_UPDATED_AT);
    ((ObjectNode) secondMessage.getRecord().getData()).remove(COL_WAKEUP);
    ((ObjectNode) secondMessage.getRecord().getData()).remove(COL_BIRTH);
    ((ObjectNode) secondMessage.getRecord().getData()).set(COL_LAST_NAME_WITH_SPACE,
        ((ObjectNode) secondMessage.getRecord().getData()).remove(COL_NAME));

    Lists.newArrayList(getTestMessages().get(0), getTestMessages().get(2));

    return Lists.newArrayList(firstMessage, secondMessage);
  }

  @Override
  protected List<AirbyteMessage> getAirbyteMessagesSecondSync(String streamName2) {
    return getTestMessages()
        .stream()
        .map(Jsons::clone)
        .peek(m -> {
          m.getRecord().setStream(streamName2);
          m.getRecord().setNamespace(getDefaultNamespace());
          ((ObjectNode) m.getRecord().getData()).remove(COL_UPDATED_AT);
          ((ObjectNode) m.getRecord().getData()).remove(COL_WAKEUP);
          ((ObjectNode) m.getRecord().getData()).remove(COL_BIRTH);
          ((ObjectNode) m.getRecord().getData()).replace(COL_ID,
              Jsons.jsonNode(m.getRecord().getData().get(COL_ID).asInt()));
        })
        .collect(Collectors.toList());
  }

  protected List<AirbyteMessage> getAirbyteMessagesSecondStreamWithNamespace(String streamName2) {
    return getTestMessages()
        .stream()
        .map(Jsons::clone)
        .peek(m -> {
          m.getRecord().setStream(streamName2);
          ((ObjectNode) m.getRecord().getData()).remove(COL_UPDATED_AT);
          ((ObjectNode) m.getRecord().getData()).remove(COL_WAKEUP);
          ((ObjectNode) m.getRecord().getData()).remove(COL_BIRTH);
          ((ObjectNode) m.getRecord().getData()).replace(COL_ID,
              Jsons.jsonNode(m.getRecord().getData().get(COL_ID).asInt()));
        })
        .collect(Collectors.toList());
  }

  protected List<AirbyteMessage> getAirbyteMessagesForTablesWithQuoting(ConfiguredAirbyteStream streamForTableWithSpaces) {
    return getTestMessages()
        .stream()
        .map(Jsons::clone)
        .peek(m -> {
          m.getRecord().setStream(streamForTableWithSpaces.getStream().getName());
          ((ObjectNode) m.getRecord().getData()).set(COL_LAST_NAME_WITH_SPACE,
              ((ObjectNode) m.getRecord().getData()).remove(COL_NAME));
          ((ObjectNode) m.getRecord().getData()).remove(COL_UPDATED_AT);
          ((ObjectNode) m.getRecord().getData()).remove(COL_BIRTH);
          ((ObjectNode) m.getRecord().getData()).remove(COL_WAKEUP);
          ((ObjectNode) m.getRecord().getData()).replace(COL_ID,
              Jsons.jsonNode(m.getRecord().getData().get(COL_ID).asInt()));
        })
        .collect(Collectors.toList());
  }

  @Override
  public boolean supportsSchemas() {
    return true;
  }

  @Override
  public AbstractJdbcSource<JDBCType> getJdbcSource() {
    return new PostgresSource();
  }

  @Override
  public JsonNode getConfig() {
    return config;
  }

  @Override
  public String getDriverClass() {
    return PostgresSource.DRIVER_CLASS;
  }

  @AfterAll
  static void cleanUp() {
    PSQL_DB.close();
  }

  @Test
  void testSpec() throws Exception {
    final ConnectorSpecification actual = source.spec();
    final ConnectorSpecification expected = Jsons.deserialize(MoreResources.readResource("spec.json"), ConnectorSpecification.class);

    assertEquals(expected, actual);
  }

  @Override
  protected List<AirbyteMessage> getTestMessages() {
    return Lists.newArrayList(
        new AirbyteMessage().withType(AirbyteMessage.Type.RECORD)
            .withRecord(new AirbyteRecordMessage().withStream(streamName).withNamespace(getDefaultNamespace())
                .withData(Jsons.jsonNode(ImmutableMap
                    .of(COL_ID, ID_VALUE_1,
                        COL_NAME, "picard",
                        COL_UPDATED_AT, "2004-10-19",
                        COL_WAKEUP, "10:10:10.123456-05:00",
                        COL_BIRTH, "2004-10-19T17:23:54.123456Z")))),
        new AirbyteMessage().withType(AirbyteMessage.Type.RECORD)
            .withRecord(new AirbyteRecordMessage().withStream(streamName).withNamespace(getDefaultNamespace())
                .withData(Jsons.jsonNode(ImmutableMap
                    .of(COL_ID, ID_VALUE_2,
                        COL_NAME, "crusher",
                        COL_UPDATED_AT, "2005-10-19",
                        COL_WAKEUP, "11:11:11.123456-05:00",
                        COL_BIRTH, "2005-10-19T17:23:54.123456Z")))),
        new AirbyteMessage().withType(AirbyteMessage.Type.RECORD)
            .withRecord(new AirbyteRecordMessage().withStream(streamName).withNamespace(getDefaultNamespace())
                .withData(Jsons.jsonNode(ImmutableMap
                    .of(COL_ID, ID_VALUE_3,
                        COL_NAME, "vash",
                        COL_UPDATED_AT, "2006-10-19",
                        COL_WAKEUP, "12:12:12.123456-05:00",
                        COL_BIRTH, "2006-10-19T17:23:54.123456Z")))));
  }

  protected void executeStatementReadIncrementallyTwice() throws SQLException {
    database.execute(connection -> {
      connection.createStatement().execute(
          String.format(
              "INSERT INTO %s(id, name, updated_at, wakeup, birth) VALUES (4,'riker', '2006-10-19','12:12:12.123456-05:00','2006-10-19T17:23:54.123456Z')",
              getFullyQualifiedTableName(TABLE_NAME)));
      connection.createStatement().execute(
          String.format(
              "INSERT INTO %s(id, name, updated_at, wakeup, birth) VALUES (5, 'data', '2006-10-19','12:12:12.123456-05:00','2006-10-19T17:23:54.123456Z')",
              getFullyQualifiedTableName(TABLE_NAME)));
    });
  }

  @Override
  protected AirbyteCatalog getCatalog(final String defaultNamespace) {
    return new AirbyteCatalog().withStreams(Lists.newArrayList(
        CatalogHelpers.createAirbyteStream(
            TABLE_NAME,
            defaultNamespace,
            Field.of(COL_ID, JsonSchemaType.NUMBER),
            Field.of(COL_NAME, JsonSchemaType.STRING),
            Field.of(COL_UPDATED_AT, JsonSchemaType.STRING_DATE),
            Field.of(COL_WAKEUP, JsonSchemaType.STRING_TIME_WITH_TIMEZONE),
            Field.of(COL_BIRTH, JsonSchemaType.STRING_TIMESTAMP_WITH_TIMEZONE))
            .withSupportedSyncModes(Lists.newArrayList(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL))
            .withSourceDefinedPrimaryKey(List.of(List.of(COL_ID))),
        CatalogHelpers.createAirbyteStream(
            TABLE_NAME_WITHOUT_PK,
            defaultNamespace,
            Field.of(COL_ID, JsonSchemaType.NUMBER),
            Field.of(COL_NAME, JsonSchemaType.STRING),
            Field.of(COL_UPDATED_AT, JsonSchemaType.STRING_DATE),
            Field.of(COL_WAKEUP, JsonSchemaType.STRING_TIME_WITH_TIMEZONE),
            Field.of(COL_BIRTH, JsonSchemaType.STRING_TIMESTAMP_WITH_TIMEZONE))
            .withSupportedSyncModes(Lists.newArrayList(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL))
            .withSourceDefinedPrimaryKey(Collections.emptyList()),
        CatalogHelpers.createAirbyteStream(
            TABLE_NAME_COMPOSITE_PK,
            defaultNamespace,
            Field.of(COL_FIRST_NAME, JsonSchemaType.STRING),
            Field.of(COL_LAST_NAME, JsonSchemaType.STRING),
            Field.of(COL_UPDATED_AT, JsonSchemaType.STRING_DATE),
            Field.of(COL_WAKEUP, JsonSchemaType.STRING_TIME_WITH_TIMEZONE),
            Field.of(COL_BIRTH, JsonSchemaType.STRING_TIMESTAMP_WITH_TIMEZONE))
            .withSupportedSyncModes(Lists.newArrayList(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL))
            .withSourceDefinedPrimaryKey(
                List.of(List.of(COL_FIRST_NAME), List.of(COL_LAST_NAME)))));
  }

  @Override
  protected void incrementalTimestampCheck() throws Exception {
    super.incrementalCursorCheck(COL_UPDATED_AT,
        "2005-10-18",
        "2006-10-19",
        Lists.newArrayList(getTestMessages().get(1),
            getTestMessages().get(2)));
  }

  @Test
  void incrementalTimeTzCheck() throws Exception {
    super.incrementalCursorCheck(COL_WAKEUP,
        "11:09:11.123456-05:00",
        "12:12:12.123456-05:00",
        Lists.newArrayList(getTestMessages().get(1),
            getTestMessages().get(2)));
  }

  @Test
  void incrementalTimestampTzCheck() throws Exception {
    super.incrementalCursorCheck(COL_BIRTH,
        "2005-10-18T17:23:54.123456Z",
        "2006-10-19T17:23:54.123456Z",
        Lists.newArrayList(getTestMessages().get(1),
            getTestMessages().get(2)));
  }

  @Override
  protected JdbcSourceOperations getSourceOperations() {
    return new PostgresSourceOperations();
  }

  @Override
  protected List<AirbyteMessage> getExpectedAirbyteMessagesSecondSync(String namespace) {
    final List<AirbyteMessage> expectedMessages = new ArrayList<>();
    expectedMessages.add(new AirbyteMessage().withType(AirbyteMessage.Type.RECORD)
        .withRecord(new AirbyteRecordMessage().withStream(streamName).withNamespace(namespace)
            .withData(Jsons.jsonNode(ImmutableMap
                .of(COL_ID, ID_VALUE_4,
                    COL_NAME, "riker",
                    COL_UPDATED_AT, "2006-10-19",
                    COL_WAKEUP, "12:12:12.123456-05:00",
                    COL_BIRTH, "2006-10-19T17:23:54.123456Z")))));
    expectedMessages.add(new AirbyteMessage().withType(AirbyteMessage.Type.RECORD)
        .withRecord(new AirbyteRecordMessage().withStream(streamName).withNamespace(namespace)
            .withData(Jsons.jsonNode(ImmutableMap
                .of(COL_ID, ID_VALUE_5,
                    COL_NAME, "data",
                    COL_UPDATED_AT, "2006-10-19",
                    COL_WAKEUP, "12:12:12.123456-05:00",
                    COL_BIRTH, "2006-10-19T17:23:54.123456Z")))));
    expectedMessages.add(new AirbyteMessage()
        .withType(AirbyteMessage.Type.STATE)
        .withState(new AirbyteStateMessage()
            .withData(Jsons.jsonNode(new DbState()
                .withCdc(false)
                .withStreams(Lists.newArrayList(new DbStreamState()
                    .withStreamName(streamName)
                    .withStreamNamespace(namespace)
                    .withCursorField(ImmutableList.of(COL_ID))
                    .withCursor("5")))))));
    return expectedMessages;
  }

}
