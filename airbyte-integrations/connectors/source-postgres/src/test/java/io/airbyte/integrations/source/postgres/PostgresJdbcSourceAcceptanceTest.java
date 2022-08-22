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
import io.airbyte.commons.features.EnvVariableFeatureFlags;
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
import io.airbyte.integrations.source.relationaldb.models.DbStreamState;
import io.airbyte.protocol.models.AirbyteCatalog;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteRecordMessage;
import io.airbyte.protocol.models.CatalogHelpers;
import io.airbyte.protocol.models.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.ConnectorSpecification;
import io.airbyte.protocol.models.Field;
import io.airbyte.protocol.models.JsonSchemaType;
import io.airbyte.protocol.models.SyncMode;
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
  public static String COL_WAKEUP_AT = "wakeup_at";
  public static String COL_LAST_VISITED_AT = "last_visited_at";
  public static String COL_LAST_COMMENT_AT = "last_comment_at";

  @BeforeAll
  static void init() {
    PSQL_DB = new PostgreSQLContainer<>("postgres:13-alpine");
    PSQL_DB.start();
    setEnv(EnvVariableFeatureFlags.USE_STREAM_CAPABLE_STATE, "true");
  }

  @Override
  @BeforeEach
  public void setup() throws Exception {
    final String dbName = Strings.addRandomSuffix("db", "_", 10).toLowerCase();
    COLUMN_CLAUSE_WITH_PK =
        "id INTEGER, name VARCHAR(200) NOT NULL, updated_at DATE NOT NULL, wakeup_at TIMETZ NOT NULL, last_visited_at TIMESTAMPTZ NOT NULL, last_comment_at TIMESTAMP NOT NULL";
    COLUMN_CLAUSE_WITHOUT_PK =
        "id INTEGER NOT NULL, name VARCHAR(200) NOT NULL, updated_at DATE NOT NULL, wakeup_at TIMETZ NOT NULL, last_visited_at TIMESTAMPTZ NOT NULL, last_comment_at TIMESTAMP NOT NULL";
    COLUMN_CLAUSE_WITH_COMPOSITE_PK =
        "first_name VARCHAR(200) NOT NULL, last_name VARCHAR(200) NOT NULL, updated_at DATE NOT NULL, wakeup_at TIMETZ NOT NULL, last_visited_at TIMESTAMPTZ NOT NULL, last_comment_at TIMESTAMP NOT NULL";

    config = Jsons.jsonNode(ImmutableMap.builder()
        .put(JdbcUtils.HOST_KEY, PSQL_DB.getHost())
        .put(JdbcUtils.PORT_KEY, PSQL_DB.getFirstMappedPort())
        .put(JdbcUtils.DATABASE_KEY, dbName)
        .put(JdbcUtils.SCHEMAS_KEY, List.of(SCHEMA_NAME, SCHEMA_NAME2))
        .put(JdbcUtils.USERNAME_KEY, PSQL_DB.getUsername())
        .put(JdbcUtils.PASSWORD_KEY, PSQL_DB.getPassword())
        .put(JdbcUtils.SSL_KEY, false)
        .build());

    final String initScriptName = "init_" + dbName.concat(".sql");
    final String tmpFilePath = IOs.writeFileToRandomTmpDir(initScriptName, "CREATE DATABASE " + dbName + ";");
    PostgreSQLContainerHelper.runSqlScript(MountableFile.forHostPath(tmpFilePath), PSQL_DB);

    source = getSource();
    final JsonNode jdbcConfig = getToDatabaseConfigFunction().apply(config);

    streamName = TABLE_NAME;

    dataSource = DataSourceFactory.create(
        jdbcConfig.get(JdbcUtils.USERNAME_KEY).asText(),
        jdbcConfig.has(JdbcUtils.PASSWORD_KEY) ? jdbcConfig.get(JdbcUtils.PASSWORD_KEY).asText() : null,
        getDriverClass(),
        jdbcConfig.get(JdbcUtils.JDBC_URL_KEY).asText(),
        JdbcUtils.parseJdbcParameters(jdbcConfig, JdbcUtils.CONNECTION_PROPERTIES_KEY, getJdbcParameterDelimiter()));

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
              "INSERT INTO %s(id, name, updated_at, wakeup_at, last_visited_at, last_comment_at) VALUES (1,'picard', '2004-10-19','10:10:10.123456-05:00','2004-10-19T17:23:54.123456Z','2004-01-01T17:23:54.123456')",
              getFullyQualifiedTableName(TABLE_NAME)));
      connection.createStatement().execute(
          String.format(
              "INSERT INTO %s(id, name, updated_at, wakeup_at, last_visited_at, last_comment_at) VALUES (2, 'crusher', '2005-10-19','11:11:11.123456-05:00','2005-10-19T17:23:54.123456Z','2005-01-01T17:23:54.123456')",
              getFullyQualifiedTableName(TABLE_NAME)));
      connection.createStatement().execute(
          String.format(
              "INSERT INTO %s(id, name, updated_at, wakeup_at, last_visited_at, last_comment_at) VALUES (3, 'vash', '2006-10-19','12:12:12.123456-05:00','2006-10-19T17:23:54.123456Z','2006-01-01T17:23:54.123456')",
              getFullyQualifiedTableName(TABLE_NAME)));

      connection.createStatement().execute(
          createTableQuery(getFullyQualifiedTableName(TABLE_NAME_WITHOUT_PK),
              COLUMN_CLAUSE_WITHOUT_PK, ""));
      connection.createStatement().execute(
          String.format(
              "INSERT INTO %s(id, name, updated_at, wakeup_at, last_visited_at, last_comment_at) VALUES (1,'picard', '2004-10-19','12:12:12.123456-05:00','2004-10-19T17:23:54.123456Z','2004-01-01T17:23:54.123456')",
              getFullyQualifiedTableName(TABLE_NAME_WITHOUT_PK)));
      connection.createStatement().execute(
          String.format(
              "INSERT INTO %s(id, name, updated_at, wakeup_at, last_visited_at, last_comment_at) VALUES (2, 'crusher', '2005-10-19','11:11:11.123456-05:00','2005-10-19T17:23:54.123456Z','2005-01-01T17:23:54.123456')",
              getFullyQualifiedTableName(TABLE_NAME_WITHOUT_PK)));
      connection.createStatement().execute(
          String.format(
              "INSERT INTO %s(id, name, updated_at, wakeup_at, last_visited_at, last_comment_at) VALUES (3, 'vash', '2006-10-19','10:10:10.123456-05:00','2006-10-19T17:23:54.123456Z','2006-01-01T17:23:54.123456')",
              getFullyQualifiedTableName(TABLE_NAME_WITHOUT_PK)));

      connection.createStatement().execute(
          createTableQuery(getFullyQualifiedTableName(TABLE_NAME_COMPOSITE_PK),
              COLUMN_CLAUSE_WITH_COMPOSITE_PK,
              primaryKeyClause(ImmutableList.of("first_name", "last_name"))));
      connection.createStatement().execute(
          String.format(
              "INSERT INTO %s(first_name, last_name, updated_at, wakeup_at, last_visited_at, last_comment_at) VALUES ('first' ,'picard', '2004-10-19','12:12:12.123456-05:00','2004-10-19T17:23:54.123456Z','2004-01-01T17:23:54.123456')",
              getFullyQualifiedTableName(TABLE_NAME_COMPOSITE_PK)));
      connection.createStatement().execute(
          String.format(
              "INSERT INTO %s(first_name, last_name, updated_at, wakeup_at, last_visited_at, last_comment_at) VALUES ('second', 'crusher', '2005-10-19','11:11:11.123456-05:00','2005-10-19T17:23:54.123456Z','2005-01-01T17:23:54.123456')",
              getFullyQualifiedTableName(TABLE_NAME_COMPOSITE_PK)));
      connection.createStatement().execute(
          String.format(
              "INSERT INTO %s(first_name, last_name, updated_at, wakeup_at, last_visited_at, last_comment_at) VALUES  ('third', 'vash', '2006-10-19','10:10:10.123456-05:00','2006-10-19T17:23:54.123456Z','2006-01-01T17:23:54.123456')",
              getFullyQualifiedTableName(TABLE_NAME_COMPOSITE_PK)));

    });

    CREATE_TABLE_WITHOUT_CURSOR_TYPE_QUERY = "CREATE TABLE %s (%s BIT(3) NOT NULL);";
    INSERT_TABLE_WITHOUT_CURSOR_TYPE_QUERY = "INSERT INTO %s VALUES(B'101');";
  }

  @Override
  protected List<AirbyteMessage> getAirbyteMessagesReadOneColumn() {
    return getTestMessages().stream()
        .map(Jsons::clone)
        .peek(m -> {
          ((ObjectNode) m.getRecord().getData()).remove(COL_NAME);
          ((ObjectNode) m.getRecord().getData()).remove(COL_UPDATED_AT);
          ((ObjectNode) m.getRecord().getData()).remove(COL_WAKEUP_AT);
          ((ObjectNode) m.getRecord().getData()).remove(COL_LAST_VISITED_AT);
          ((ObjectNode) m.getRecord().getData()).remove(COL_LAST_COMMENT_AT);
          ((ObjectNode) m.getRecord().getData()).replace(COL_ID,
              Jsons.jsonNode(m.getRecord().getData().get(COL_ID).asInt()));
        })
        .collect(Collectors.toList());
  }

  @Override
  protected ArrayList<AirbyteMessage> getAirbyteMessagesCheckCursorSpaceInColumnName(final ConfiguredAirbyteStream streamWithSpaces) {
    final AirbyteMessage firstMessage = getTestMessages().get(0);
    firstMessage.getRecord().setStream(streamWithSpaces.getStream().getName());
    ((ObjectNode) firstMessage.getRecord().getData()).remove(COL_UPDATED_AT);
    ((ObjectNode) firstMessage.getRecord().getData()).remove(COL_WAKEUP_AT);
    ((ObjectNode) firstMessage.getRecord().getData()).remove(COL_LAST_VISITED_AT);
    ((ObjectNode) firstMessage.getRecord().getData()).remove(COL_LAST_COMMENT_AT);
    ((ObjectNode) firstMessage.getRecord().getData()).set(COL_LAST_NAME_WITH_SPACE,
        ((ObjectNode) firstMessage.getRecord().getData()).remove(COL_NAME));

    final AirbyteMessage secondMessage = getTestMessages().get(2);
    secondMessage.getRecord().setStream(streamWithSpaces.getStream().getName());
    ((ObjectNode) secondMessage.getRecord().getData()).remove(COL_UPDATED_AT);
    ((ObjectNode) secondMessage.getRecord().getData()).remove(COL_WAKEUP_AT);
    ((ObjectNode) secondMessage.getRecord().getData()).remove(COL_LAST_VISITED_AT);
    ((ObjectNode) secondMessage.getRecord().getData()).remove(COL_LAST_COMMENT_AT);
    ((ObjectNode) secondMessage.getRecord().getData()).set(COL_LAST_NAME_WITH_SPACE,
        ((ObjectNode) secondMessage.getRecord().getData()).remove(COL_NAME));

    Lists.newArrayList(getTestMessages().get(0), getTestMessages().get(2));

    return Lists.newArrayList(firstMessage, secondMessage);
  }

  @Override
  protected List<AirbyteMessage> getAirbyteMessagesSecondSync(final String streamName2) {
    return getTestMessages()
        .stream()
        .map(Jsons::clone)
        .peek(m -> {
          m.getRecord().setStream(streamName2);
          m.getRecord().setNamespace(getDefaultNamespace());
          ((ObjectNode) m.getRecord().getData()).remove(COL_UPDATED_AT);
          ((ObjectNode) m.getRecord().getData()).remove(COL_WAKEUP_AT);
          ((ObjectNode) m.getRecord().getData()).remove(COL_LAST_VISITED_AT);
          ((ObjectNode) m.getRecord().getData()).remove(COL_LAST_COMMENT_AT);
          ((ObjectNode) m.getRecord().getData()).replace(COL_ID,
              Jsons.jsonNode(m.getRecord().getData().get(COL_ID).asInt()));
        })
        .collect(Collectors.toList());
  }

  @Override
  protected List<AirbyteMessage> getAirbyteMessagesSecondStreamWithNamespace(final String streamName2) {
    return getTestMessages()
        .stream()
        .map(Jsons::clone)
        .peek(m -> {
          m.getRecord().setStream(streamName2);
          ((ObjectNode) m.getRecord().getData()).remove(COL_UPDATED_AT);
          ((ObjectNode) m.getRecord().getData()).remove(COL_WAKEUP_AT);
          ((ObjectNode) m.getRecord().getData()).remove(COL_LAST_VISITED_AT);
          ((ObjectNode) m.getRecord().getData()).remove(COL_LAST_COMMENT_AT);
          ((ObjectNode) m.getRecord().getData()).replace(COL_ID,
              Jsons.jsonNode(m.getRecord().getData().get(COL_ID).asInt()));
        })
        .collect(Collectors.toList());
  }

  @Override
  protected List<AirbyteMessage> getAirbyteMessagesForTablesWithQuoting(final ConfiguredAirbyteStream streamForTableWithSpaces) {
    return getTestMessages()
        .stream()
        .map(Jsons::clone)
        .peek(m -> {
          m.getRecord().setStream(streamForTableWithSpaces.getStream().getName());
          ((ObjectNode) m.getRecord().getData()).set(COL_LAST_NAME_WITH_SPACE,
              ((ObjectNode) m.getRecord().getData()).remove(COL_NAME));
          ((ObjectNode) m.getRecord().getData()).remove(COL_UPDATED_AT);
          ((ObjectNode) m.getRecord().getData()).remove(COL_LAST_VISITED_AT);
          ((ObjectNode) m.getRecord().getData()).remove(COL_LAST_COMMENT_AT);
          ((ObjectNode) m.getRecord().getData()).remove(COL_WAKEUP_AT);
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
                        COL_WAKEUP_AT, "10:10:10.123456-05:00",
                        COL_LAST_VISITED_AT, "2004-10-19T17:23:54.123456Z",
                        COL_LAST_COMMENT_AT, "2004-01-01T17:23:54.123456")))),
        new AirbyteMessage().withType(AirbyteMessage.Type.RECORD)
            .withRecord(new AirbyteRecordMessage().withStream(streamName).withNamespace(getDefaultNamespace())
                .withData(Jsons.jsonNode(ImmutableMap
                    .of(COL_ID, ID_VALUE_2,
                        COL_NAME, "crusher",
                        COL_UPDATED_AT, "2005-10-19",
                        COL_WAKEUP_AT, "11:11:11.123456-05:00",
                        COL_LAST_VISITED_AT, "2005-10-19T17:23:54.123456Z",
                        COL_LAST_COMMENT_AT, "2005-01-01T17:23:54.123456")))),
        new AirbyteMessage().withType(AirbyteMessage.Type.RECORD)
            .withRecord(new AirbyteRecordMessage().withStream(streamName).withNamespace(getDefaultNamespace())
                .withData(Jsons.jsonNode(ImmutableMap
                    .of(COL_ID, ID_VALUE_3,
                        COL_NAME, "vash",
                        COL_UPDATED_AT, "2006-10-19",
                        COL_WAKEUP_AT, "12:12:12.123456-05:00",
                        COL_LAST_VISITED_AT, "2006-10-19T17:23:54.123456Z",
                        COL_LAST_COMMENT_AT, "2006-01-01T17:23:54.123456")))));
  }

  @Override
  protected void executeStatementReadIncrementallyTwice() throws SQLException {
    database.execute(connection -> {
      connection.createStatement().execute(
          String.format(
              "INSERT INTO %s(id, name, updated_at, wakeup_at, last_visited_at, last_comment_at) VALUES (4,'riker', '2006-10-19','12:12:12.123456-05:00','2006-10-19T17:23:54.123456Z','2006-01-01T17:23:54.123456')",
              getFullyQualifiedTableName(TABLE_NAME)));
      connection.createStatement().execute(
          String.format(
              "INSERT INTO %s(id, name, updated_at, wakeup_at, last_visited_at, last_comment_at) VALUES (5, 'data', '2006-10-19','12:12:12.123456-05:00','2006-10-19T17:23:54.123456Z','2006-01-01T17:23:54.123456')",
              getFullyQualifiedTableName(TABLE_NAME)));
    });
  }

  @Override
  protected AirbyteCatalog getCatalog(final String defaultNamespace) {
    return new AirbyteCatalog().withStreams(Lists.newArrayList(
        CatalogHelpers.createAirbyteStream(
            TABLE_NAME,
            defaultNamespace,
            Field.of(COL_ID, JsonSchemaType.INTEGER),
            Field.of(COL_NAME, JsonSchemaType.STRING),
            Field.of(COL_UPDATED_AT, JsonSchemaType.STRING_DATE),
            Field.of(COL_WAKEUP_AT, JsonSchemaType.STRING_TIME_WITH_TIMEZONE),
            Field.of(COL_LAST_VISITED_AT, JsonSchemaType.STRING_TIMESTAMP_WITH_TIMEZONE),
            Field.of(COL_LAST_COMMENT_AT, JsonSchemaType.STRING_TIMESTAMP_WITHOUT_TIMEZONE))
            .withSupportedSyncModes(Lists.newArrayList(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL))
            .withSourceDefinedPrimaryKey(List.of(List.of(COL_ID))),
        CatalogHelpers.createAirbyteStream(
            TABLE_NAME_WITHOUT_PK,
            defaultNamespace,
            Field.of(COL_ID, JsonSchemaType.INTEGER),
            Field.of(COL_NAME, JsonSchemaType.STRING),
            Field.of(COL_UPDATED_AT, JsonSchemaType.STRING_DATE),
            Field.of(COL_WAKEUP_AT, JsonSchemaType.STRING_TIME_WITH_TIMEZONE),
            Field.of(COL_LAST_VISITED_AT, JsonSchemaType.STRING_TIMESTAMP_WITH_TIMEZONE),
            Field.of(COL_LAST_COMMENT_AT, JsonSchemaType.STRING_TIMESTAMP_WITHOUT_TIMEZONE))
            .withSupportedSyncModes(Lists.newArrayList(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL))
            .withSourceDefinedPrimaryKey(Collections.emptyList()),
        CatalogHelpers.createAirbyteStream(
            TABLE_NAME_COMPOSITE_PK,
            defaultNamespace,
            Field.of(COL_FIRST_NAME, JsonSchemaType.STRING),
            Field.of(COL_LAST_NAME, JsonSchemaType.STRING),
            Field.of(COL_UPDATED_AT, JsonSchemaType.STRING_DATE),
            Field.of(COL_WAKEUP_AT, JsonSchemaType.STRING_TIME_WITH_TIMEZONE),
            Field.of(COL_LAST_VISITED_AT, JsonSchemaType.STRING_TIMESTAMP_WITH_TIMEZONE),
            Field.of(COL_LAST_COMMENT_AT, JsonSchemaType.STRING_TIMESTAMP_WITHOUT_TIMEZONE))
            .withSupportedSyncModes(Lists.newArrayList(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL))
            .withSourceDefinedPrimaryKey(
                List.of(List.of(COL_FIRST_NAME), List.of(COL_LAST_NAME)))));
  }

  @Override
  protected void incrementalDateCheck() throws Exception {
    super.incrementalCursorCheck(COL_UPDATED_AT,
        "2005-10-18",
        "2006-10-19",
        Lists.newArrayList(getTestMessages().get(1),
            getTestMessages().get(2)));
  }

  @Test
  void incrementalTimeTzCheck() throws Exception {
    super.incrementalCursorCheck(COL_WAKEUP_AT,
        "11:09:11.123456-05:00",
        "12:12:12.123456-05:00",
        Lists.newArrayList(getTestMessages().get(1),
            getTestMessages().get(2)));
  }

  @Test
  void incrementalTimestampTzCheck() throws Exception {
    super.incrementalCursorCheck(COL_LAST_VISITED_AT,
        "2005-10-18T17:23:54.123456Z",
        "2006-10-19T17:23:54.123456Z",
        Lists.newArrayList(getTestMessages().get(1),
            getTestMessages().get(2)));
  }

  @Test
  void incrementalTimestampCheck() throws Exception {
    super.incrementalCursorCheck(COL_LAST_COMMENT_AT,
        "2004-12-12T17:23:54.123456",
        "2006-01-01T17:23:54.123456",
        Lists.newArrayList(getTestMessages().get(1),
            getTestMessages().get(2)));
  }

  @Override
  protected JdbcSourceOperations getSourceOperations() {
    return new PostgresSourceOperations();
  }

  @Override
  protected List<AirbyteMessage> getExpectedAirbyteMessagesSecondSync(final String namespace) {
    final List<AirbyteMessage> expectedMessages = new ArrayList<>();
    expectedMessages.add(new AirbyteMessage().withType(AirbyteMessage.Type.RECORD)
        .withRecord(new AirbyteRecordMessage().withStream(streamName).withNamespace(namespace)
            .withData(Jsons.jsonNode(ImmutableMap
                .of(COL_ID, ID_VALUE_4,
                    COL_NAME, "riker",
                    COL_UPDATED_AT, "2006-10-19",
                    COL_WAKEUP_AT, "12:12:12.123456-05:00",
                    COL_LAST_VISITED_AT, "2006-10-19T17:23:54.123456Z",
                    COL_LAST_COMMENT_AT, "2006-01-01T17:23:54.123456")))));
    expectedMessages.add(new AirbyteMessage().withType(AirbyteMessage.Type.RECORD)
        .withRecord(new AirbyteRecordMessage().withStream(streamName).withNamespace(namespace)
            .withData(Jsons.jsonNode(ImmutableMap
                .of(COL_ID, ID_VALUE_5,
                    COL_NAME, "data",
                    COL_UPDATED_AT, "2006-10-19",
                    COL_WAKEUP_AT, "12:12:12.123456-05:00",
                    COL_LAST_VISITED_AT, "2006-10-19T17:23:54.123456Z",
                    COL_LAST_COMMENT_AT, "2006-01-01T17:23:54.123456")))));
    final DbStreamState state = new DbStreamState()
        .withStreamName(streamName)
        .withStreamNamespace(namespace)
        .withCursorField(ImmutableList.of(COL_ID))
        .withCursor("5");
    expectedMessages.addAll(createExpectedTestMessages(List.of(state)));
    return expectedMessages;
  }

  @Override
  protected boolean supportsPerStream() {
    return true;
  }

}
