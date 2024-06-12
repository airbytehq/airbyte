/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.oracle_strict_encrypt;

import static io.airbyte.cdk.integrations.source.relationaldb.RelationalDbQueryUtils.enquoteIdentifier;
import static org.junit.Assert.assertEquals;
import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableList;
import com.google.common.collect.ImmutableMap;
import com.google.common.collect.ImmutableSet;
import com.google.common.collect.Lists;
import io.airbyte.cdk.integrations.base.ssh.SshHelpers;
import io.airbyte.cdk.integrations.source.jdbc.test.JdbcSourceAcceptanceTest;
import io.airbyte.cdk.integrations.source.relationaldb.models.DbState;
import io.airbyte.cdk.integrations.source.relationaldb.models.DbStreamState;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.commons.util.MoreIterators;
import io.airbyte.protocol.models.Field;
import io.airbyte.protocol.models.JsonSchemaType;
import io.airbyte.protocol.models.v0.AirbyteCatalog;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteMessage.Type;
import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
import io.airbyte.protocol.models.v0.AirbyteStateMessage;
import io.airbyte.protocol.models.v0.AirbyteStreamState;
import io.airbyte.protocol.models.v0.CatalogHelpers;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.ConnectorSpecification;
import io.airbyte.protocol.models.v0.DestinationSyncMode;
import io.airbyte.protocol.models.v0.StreamDescriptor;
import io.airbyte.protocol.models.v0.SyncMode;
import java.math.BigDecimal;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Optional;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Disabled;
import org.junit.jupiter.api.Test;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

@Disabled
class OracleStrictEncryptJdbcSourceAcceptanceTest extends JdbcSourceAcceptanceTest<OracleStrictEncryptSource, OracleStrictEncryptTestDatabase> {

  private static final Logger LOGGER = LoggerFactory.getLogger(OracleStrictEncryptJdbcSourceAcceptanceTest.class);
  private static final AirbyteOracleTestContainer ORACLE_DB = new AirbyteOracleTestContainer()
      .withEnv("NLS_DATE_FORMAT", "YYYY-MM-DD")
      .withEnv("RELAX_SECURITY", "1")
      .withUsername("TEST_ORA")
      .withPassword("oracle")
      .usingSid()
      .withEnv("RELAX_SECURITY", "1");

  @BeforeAll
  static void init() {
    SCHEMA_NAME = "JDBC_INTEGRATION_TEST1";
    SCHEMA_NAME2 = "JDBC_INTEGRATION_TEST2";
    TEST_SCHEMAS = ImmutableSet.of(SCHEMA_NAME, SCHEMA_NAME2);

    TABLE_NAME = "ID_AND_NAME";
    TABLE_NAME_WITH_SPACES = "ID AND NAME";
    TABLE_NAME_WITHOUT_PK = "ID_AND_NAME_WITHOUT_PK";
    TABLE_NAME_COMPOSITE_PK = "FULL_NAME_COMPOSITE_PK";
    TABLE_NAME_AND_TIMESTAMP = "NAME_AND_TIMESTAMP";
    COL_ID = "ID";
    COL_NAME = "NAME";
    COL_UPDATED_AT = "UPDATED_AT";
    COL_FIRST_NAME = "FIRST_NAME";
    COL_LAST_NAME = "LAST_NAME";
    COL_LAST_NAME_WITH_SPACE = "LAST NAME";
    COL_TIMESTAMP = "TIMESTAMP";
    ID_VALUE_1 = new BigDecimal(1);
    ID_VALUE_2 = new BigDecimal(2);
    ID_VALUE_3 = new BigDecimal(3);
    ID_VALUE_4 = new BigDecimal(4);
    ID_VALUE_5 = new BigDecimal(5);
    CREATE_TABLE_WITHOUT_CURSOR_TYPE_QUERY = "CREATE TABLE %s (%s CLOB)";
    INSERT_TABLE_WITHOUT_CURSOR_TYPE_QUERY = "INSERT INTO %s VALUES(to_clob('clob data'))";
    CREATE_TABLE_WITH_NULLABLE_CURSOR_TYPE_QUERY = "CREATE TABLE %s (%s VARCHAR(20))";
    INSERT_TABLE_WITH_NULLABLE_CURSOR_TYPE_QUERY = "INSERT INTO %s VALUES('Hello world :)')";
    INSERT_TABLE_NAME_AND_TIMESTAMP_QUERY = "INSERT INTO %s (name, timestamp) VALUES ('%s', TO_TIMESTAMP('%s', 'YYYY-MM-DD HH24:MI:SS'))";
  }

  @Override
  protected void incrementalDateCheck() throws Exception {
    // https://stackoverflow.com/questions/47712930/resultset-meta-data-return-timestamp-instead-of-date-oracle-jdbc
    // Oracle DATE is a java.sql.Timestamp (java.sql.Types.TIMESTAMP) as far as JDBC (and the SQL
    // standard) is concerned as it has both a date and time component.
    incrementalCursorCheck(
        COL_UPDATED_AT,
        "2005-10-18T00:00:00.000000",
        "2006-10-19T00:00:00.000000",
        Lists.newArrayList(getTestMessages().get(1), getTestMessages().get(2)));
  }

  static void cleanUpTables() throws SQLException {
    final Connection connection = DriverManager.getConnection(
        ORACLE_DB.getJdbcUrl(),
        ORACLE_DB.getUsername(),
        ORACLE_DB.getPassword());
    for (final String schemaName : TEST_SCHEMAS) {
      final ResultSet resultSet =
          connection.createStatement().executeQuery(String.format("SELECT TABLE_NAME FROM ALL_TABLES WHERE OWNER = '%s'", schemaName));
      while (resultSet.next()) {
        final String tableName = resultSet.getString("TABLE_NAME");
        final String tableNameProcessed =
            tableName.contains(" ") ? enquoteIdentifier(tableName, connection.getMetaData().getIdentifierQuoteString())
                : tableName;
        connection.createStatement().executeQuery("DROP TABLE " + schemaName + "." + tableNameProcessed);
      }
    }
    if (!connection.isClosed())
      connection.close();
  }

  @Override
  protected OracleStrictEncryptTestDatabase createTestDatabase() {
    ORACLE_DB.start();
    return new OracleStrictEncryptTestDatabase(ORACLE_DB, List.of(SCHEMA_NAME, SCHEMA_NAME2)).initialized();
  }

  @Override
  public boolean supportsSchemas() {
    // See https://www.oratable.com/oracle-user-schema-difference/
    return true;
  }

  @Override
  protected OracleStrictEncryptSource source() {
    return new OracleStrictEncryptSource();
  }

  @Override
  public JsonNode config() {
    return Jsons.clone(testdb.configBuilder().build());
  }

  @AfterAll
  static void cleanUp() {
    ORACLE_DB.close();
  }

  @Override
  public void createSchemas() {
    // In Oracle, `CREATE USER` creates a schema.
    // See https://www.oratable.com/oracle-user-schema-difference/
    if (supportsSchemas()) {
      for (final String schemaName : TEST_SCHEMAS) {
        executeOracleStatement(
            String.format(
                "CREATE USER %s IDENTIFIED BY password DEFAULT TABLESPACE USERS QUOTA UNLIMITED ON USERS",
                schemaName));
      }
    }
  }

  static void cleanUpTablesAndWait() {
    try {
      cleanUpTables();
      Thread.sleep(1000);
    } catch (final Exception e) {
      throw new RuntimeException(e);
    }
  }

  public void executeOracleStatement(final String query) {
    try (final Connection connection = DriverManager.getConnection(
        ORACLE_DB.getJdbcUrl(),
        ORACLE_DB.getUsername(),
        ORACLE_DB.getPassword());
        final Statement stmt = connection.createStatement()) {
      stmt.execute(query);
    } catch (final SQLException e) {
      logSQLException(e);
    }
  }

  public static void logSQLException(final SQLException ex) {
    for (final Throwable e : ex) {
      if (e instanceof final SQLException sqlException) {
        if (!ignoreSQLException(sqlException.getSQLState())) {
          LOGGER.info("SQLState: " + ((SQLException) e).getSQLState());
          LOGGER.info("Error Code: " + ((SQLException) e).getErrorCode());
          LOGGER.info("Message: " + e.getMessage());
          Throwable t = ex.getCause();
          while (t != null) {
            LOGGER.info("Cause: " + t);
            t = t.getCause();
          }
        }
      }
    }
  }

  public static boolean ignoreSQLException(final String sqlState) {
    // This only ignore cases where other databases won't raise errors
    // Drop table, schema etc or try to recreate a table;
    if (sqlState == null) {
      LOGGER.info("The SQL state is not defined!");
      return false;
    }
    // X0Y32: Jar file already exists in schema
    if (sqlState.equalsIgnoreCase("X0Y32")) {
      return true;
    }
    // 42Y55: Table already exists in schema
    if (sqlState.equalsIgnoreCase("42Y55")) {
      return true;
    }
    // 42000: User name already exists
    if (sqlState.equalsIgnoreCase("42000")) {
      return true;
    }

    return false;
  }

  @Test
  void testSpec() throws Exception {
    final ConnectorSpecification actual = source().spec();
    final ConnectorSpecification expected =
        SshHelpers.injectSshIntoSpec(Jsons.deserialize(MoreResources.readResource("expected_spec.json"), ConnectorSpecification.class));
    assertEquals(expected, actual);
  }

  @Override
  protected AirbyteCatalog getCatalog(final String defaultNamespace) {
    return new AirbyteCatalog().withStreams(List.of(
        CatalogHelpers.createAirbyteStream(
            TABLE_NAME,
            defaultNamespace,
            Field.of(COL_ID, JsonSchemaType.NUMBER),
            Field.of(COL_NAME, JsonSchemaType.STRING),
            Field.of(COL_UPDATED_AT, JsonSchemaType.STRING))
            .withSupportedSyncModes(List.of(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL))
            .withSourceDefinedPrimaryKey(List.of(List.of(COL_ID))),
        CatalogHelpers.createAirbyteStream(
            TABLE_NAME_WITHOUT_PK,
            defaultNamespace,
            Field.of(COL_ID, JsonSchemaType.NUMBER),
            Field.of(COL_NAME, JsonSchemaType.STRING),
            Field.of(COL_UPDATED_AT, JsonSchemaType.STRING))
            .withSupportedSyncModes(List.of(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL))
            .withSourceDefinedPrimaryKey(Collections.emptyList()),
        CatalogHelpers.createAirbyteStream(
            TABLE_NAME_COMPOSITE_PK,
            defaultNamespace,
            Field.of(COL_FIRST_NAME, JsonSchemaType.STRING),
            Field.of(COL_LAST_NAME, JsonSchemaType.STRING),
            Field.of(COL_UPDATED_AT, JsonSchemaType.STRING))
            .withSupportedSyncModes(List.of(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL))
            .withSourceDefinedPrimaryKey(
                List.of(List.of(COL_FIRST_NAME), List.of(COL_LAST_NAME)))));
  }

  @Override
  protected List<AirbyteMessage> getTestMessages() {
    return Lists.newArrayList(
        new AirbyteMessage().withType(Type.RECORD)
            .withRecord(new AirbyteRecordMessage().withStream(streamName())
                .withNamespace(getDefaultNamespace())
                .withData(Jsons.jsonNode(ImmutableMap
                    .of(COL_ID, ID_VALUE_1,
                        COL_NAME, "picard",
                        COL_UPDATED_AT, "2004-10-19T00:00:00.000000")))),
        new AirbyteMessage().withType(Type.RECORD)
            .withRecord(new AirbyteRecordMessage().withStream(streamName())
                .withNamespace(getDefaultNamespace())
                .withData(Jsons.jsonNode(ImmutableMap
                    .of(COL_ID, ID_VALUE_2,
                        COL_NAME, "crusher",
                        COL_UPDATED_AT,
                        "2005-10-19T00:00:00.000000")))),
        new AirbyteMessage().withType(Type.RECORD)
            .withRecord(new AirbyteRecordMessage().withStream(streamName())
                .withNamespace(getDefaultNamespace())
                .withData(Jsons.jsonNode(ImmutableMap
                    .of(COL_ID, ID_VALUE_3,
                        COL_NAME, "vash",
                        COL_UPDATED_AT, "2006-10-19T00:00:00.000000")))));
  }

  @Test
  @Override
  protected void testReadOneTableIncrementallyTwice() throws Exception {
    final String namespace = getDefaultNamespace();
    final ConfiguredAirbyteCatalog configuredCatalog = getConfiguredCatalogWithOneStream(namespace);
    configuredCatalog.getStreams().forEach(airbyteStream -> {
      airbyteStream.setSyncMode(SyncMode.INCREMENTAL);
      airbyteStream.setCursorField(Lists.newArrayList(COL_ID));
      airbyteStream.setDestinationSyncMode(DestinationSyncMode.APPEND);
    });

    final DbState state = new DbState()
        .withStreams(Lists.newArrayList(new DbStreamState().withStreamName(streamName()).withStreamNamespace(namespace)));
    final List<AirbyteMessage> actualMessagesFirstSync = MoreIterators
        .toList(source().read(config(), configuredCatalog, Jsons.jsonNode(state)));

    final Optional<AirbyteMessage> stateAfterFirstSyncOptional = actualMessagesFirstSync.stream()
        .filter(r -> r.getType() == Type.STATE).findFirst();
    assertTrue(stateAfterFirstSyncOptional.isPresent());

    testdb.with(String.format("INSERT INTO %s(id, name, updated_at) VALUES (4,'riker', '2006-10-19')",
        getFullyQualifiedTableName(TABLE_NAME)));
    testdb.with(String.format("INSERT INTO %s(id, name, updated_at) VALUES (5, 'data', '2006-10-19')",
        getFullyQualifiedTableName(TABLE_NAME)));

    final List<AirbyteMessage> actualMessagesSecondSync = MoreIterators
        .toList(source().read(config(), configuredCatalog,
            stateAfterFirstSyncOptional.get().getState().getData()));

    Assertions.assertEquals(2,
        (int) actualMessagesSecondSync.stream().filter(r -> r.getType() == Type.RECORD).count());
    final List<AirbyteMessage> expectedMessages = new ArrayList<>();
    expectedMessages.add(new AirbyteMessage().withType(Type.RECORD)
        .withRecord(new AirbyteRecordMessage().withStream(streamName()).withNamespace(namespace)
            .withData(Jsons.jsonNode(ImmutableMap
                .of(COL_ID, ID_VALUE_4,
                    COL_NAME, "riker",
                    COL_UPDATED_AT, "2006-10-19T00:00:00.000000")))));
    expectedMessages.add(new AirbyteMessage().withType(Type.RECORD)
        .withRecord(new AirbyteRecordMessage().withStream(streamName()).withNamespace(namespace)
            .withData(Jsons.jsonNode(ImmutableMap
                .of(COL_ID, ID_VALUE_5,
                    COL_NAME, "data",
                    COL_UPDATED_AT, "2006-10-19T00:00:00.000000")))));
    expectedMessages.add(new AirbyteMessage()
        .withType(Type.STATE)
        .withState(new AirbyteStateMessage()
            .withType(AirbyteStateMessage.AirbyteStateType.STREAM)
            .withStream(new AirbyteStreamState()
                .withStreamDescriptor(new StreamDescriptor().withName(streamName()).withNamespace(namespace))
                .withStreamState(Jsons.jsonNode(new DbStreamState()
                    .withStreamNamespace(namespace)
                    .withStreamName(streamName())
                    .withCursorField(ImmutableList.of(COL_ID))
                    .withCursor("5")
                    .withCursorRecordCount(1L))))
            .withData(Jsons.jsonNode(new DbState()
                .withCdc(false)
                .withStreams(Lists.newArrayList(new DbStreamState()
                    .withStreamName(streamName())
                    .withStreamNamespace(namespace)
                    .withCursorField(ImmutableList.of(COL_ID))
                    .withCursor("5")
                    .withCursorRecordCount(1L)))))));

    setEmittedAtToNull(actualMessagesSecondSync);

    assertArrayEquals(expectedMessages.toArray(), actualMessagesSecondSync.toArray());
    assertTrue(expectedMessages.containsAll(actualMessagesSecondSync));
    assertTrue(actualMessagesSecondSync.containsAll(expectedMessages));
  }

  @Test
  void testIncrementalTimestampCheckCursor() throws Exception {
    incrementalCursorCheck(
        COL_UPDATED_AT,
        "2005-10-18T00:00:00.000000",
        "2006-10-19T00:00:00.000000",
        Lists.newArrayList(getTestMessages().get(1), getTestMessages().get(2)));
  }

}
