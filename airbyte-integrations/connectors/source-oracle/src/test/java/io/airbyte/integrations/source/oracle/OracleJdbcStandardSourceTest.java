/*
 * MIT License
 *
 * Copyright (c) 2020 Airbyte
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 */

package io.airbyte.integrations.source.oracle;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.collect.ImmutableList;
import com.google.common.collect.ImmutableMap;
import com.google.common.collect.ImmutableSet;
import com.google.common.collect.Lists;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.util.MoreIterators;
import io.airbyte.db.Databases;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.db.jdbc.JdbcUtils;
import io.airbyte.integrations.source.jdbc.AbstractJdbcSource;
import io.airbyte.integrations.source.jdbc.models.JdbcState;
import io.airbyte.integrations.source.jdbc.models.JdbcStreamState;
import io.airbyte.integrations.source.jdbc.test.JdbcSourceStandardTest;
import io.airbyte.protocol.models.*;
import org.junit.jupiter.api.*;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import static org.junit.jupiter.api.Assertions.assertTrue;

import org.testcontainers.containers.OracleContainer;

import java.sql.*;
import java.util.*;
import java.util.stream.Collectors;

class OracleJdbcStandardSourceTest extends JdbcSourceStandardTest {
  private static final String SCHEMA_NAME = "JDBC_INTEGRATION_TEST";
  private static final String SCHEMA_NAME2 = "JDBC_INTEGRATION_TEST2";
  private static final Set<String> TEST_SCHEMAS = ImmutableSet.of(SCHEMA_NAME, SCHEMA_NAME2);
  private static final Logger LOGGER = LoggerFactory.getLogger(OracleSource.class);
  private static OracleContainer ORACLE_DB;

  private JsonNode config;
    private JdbcDatabase database;

  @BeforeAll
  static void init() throws SQLException {
    ORACLE_DB = new OracleContainer("epiclabs/docker-oracle-xe-11g");
    ORACLE_DB.start();
    }

  @BeforeEach
  public void setup() throws Exception {

    config = Jsons.jsonNode(ImmutableMap.builder()
            .put("host", ORACLE_DB.getHost())
            .put("port", ORACLE_DB.getFirstMappedPort())
            .put("sid", ORACLE_DB.getSid())
            .put("username", ORACLE_DB.getUsername())
            .put("password", ORACLE_DB.getPassword())
            .build());

    //executeOracleStatement("ALTER SESSION SET NLS_DATE_FORMAT = 'YYYY-MM-DD'");

    //super.setup();

    AbstractJdbcSource source = getSource();
    JsonNode config = getConfig();
    final JsonNode jdbcConfig = source.toJdbcConfig(config);

    String streamName = getDefaultNamespace() + "." + TABLE_NAME;

    database = Databases.createJdbcDatabase(
              jdbcConfig.get("username").asText(),
              jdbcConfig.has("password") ? jdbcConfig.get("password").asText() : null,
              jdbcConfig.get("jdbc_url").asText(),
              getDriverClass());

      if (supportsSchemas()) {
          createSchemas();
      }

      if (getDriverClass().toLowerCase().contains("oracle")) {
          executeOracleStatement(String.format("DROP TABLE %s", getFullyQualifiedTableName(TABLE_NAME)));
      }

      database.execute(connection -> {
          connection.createStatement().execute("ALTER SESSION SET NLS_DATE_FORMAT = 'YYYY-MM-DD'");
          connection.createStatement()
                  .execute(String.format("CREATE TABLE %s(ID INTEGER, NAME VARCHAR(200), UPDATED_AT DATE)", getFullyQualifiedTableName(TABLE_NAME)));
          connection.createStatement().execute(
                  String.format("INSERT INTO %s(id, name, updated_at) VALUES (1,'picard', '2004-10-19')", getFullyQualifiedTableName(TABLE_NAME)));
          connection.createStatement().execute(
                  String.format("INSERT INTO %s(id, name, updated_at) VALUES (2, 'crusher', '2005-10-19')", getFullyQualifiedTableName(TABLE_NAME)));
          connection.createStatement().execute(
                  String.format("INSERT INTO %s(id, name, updated_at) VALUES (3, 'vash', '2006-10-19')", getFullyQualifiedTableName(TABLE_NAME)));
      });
  }

    @Override
    public void testReadMultipleTables() throws Exception {
        final ConfiguredAirbyteCatalog catalog =
                new ConfiguredAirbyteCatalog().withStreams(Lists.newArrayList(getConfiguredCatalog().getStreams().get(0)));
        final List<AirbyteMessage> expectedMessages = new ArrayList<>(getTestMessages());

        for (int i = 2; i < 10; i++) {
            final int iFinal = i;
            final String streamName2 = streamName + i;
            database.execute(connection -> {
                connection.createStatement()
                        .execute(String.format("CREATE TABLE %s(id INTEGER, name VARCHAR(200))", getFullyQualifiedTableName(TABLE_NAME + iFinal)));
                connection.createStatement().execute(String.format("INSERT INTO %s(id, name) VALUES (1,'picard')",
                        getFullyQualifiedTableName(TABLE_NAME + iFinal)));
                connection.createStatement().execute(String.format("INSERT INTO %s(id, name) VALUES (2, 'crusher')",
                        getFullyQualifiedTableName(TABLE_NAME + iFinal)));
                connection.createStatement().execute(String.format("INSERT INTO %s(id, name) VALUES (3, 'vash')",
                        getFullyQualifiedTableName(TABLE_NAME + iFinal)));
            });

            catalog.getStreams().add(CatalogHelpers.createConfiguredAirbyteStream(
                    streamName2,
                    Field.of("ID", Field.JsonSchemaPrimitive.NUMBER),
                    Field.of("NAME", Field.JsonSchemaPrimitive.STRING)));

            final List<AirbyteMessage> secondStreamExpectedMessages = getTestMessages()
                    .stream()
                    .map(Jsons::clone)
                    .peek(m -> {
                        m.getRecord().setStream(streamName2);
                        ((ObjectNode) m.getRecord().getData()).remove("UPDATED_AT");
                    })
                    .collect(Collectors.toList());
            expectedMessages.addAll(secondStreamExpectedMessages);
        }

        final List<AirbyteMessage> actualMessages = MoreIterators.toList(source.read(config, catalog, null));

        setEmittedAtToNull(actualMessages);

        AirbyteMessage firstExpectedMsg = expectedMessages.get(0);
        AirbyteMessage firstActualMsg = actualMessages.get(0);

        boolean checkFirstAreEqual = firstExpectedMsg.equals(firstExpectedMsg);
        int hashFirstExpected = firstExpectedMsg.hashCode();
        int hashFirstActual = firstActualMsg.hashCode();
        boolean hashAreEqual =  hashFirstExpected == hashFirstActual;


        Assertions.assertEquals(expectedMessages, actualMessages);
    }

    @Override
    public void testReadMultipleTablesIncrementally() throws Exception {
        final String tableName2 = TABLE_NAME + 20;
        final String streamName2 = streamName + 2;
        database.execute(ctx -> {
            ctx.createStatement().execute(String.format("CREATE TABLE %s(id INTEGER, name VARCHAR(200))", getFullyQualifiedTableName(tableName2)));
            ctx.createStatement().execute(
                    String.format("INSERT INTO %s(id, name) VALUES (1,'picard')", getFullyQualifiedTableName(tableName2)));
            ctx.createStatement().execute(
                    String.format("INSERT INTO %s(id, name) VALUES (2, 'crusher')", getFullyQualifiedTableName(tableName2)));
            ctx.createStatement().execute(
                    String.format("INSERT INTO %s(id, name) VALUES (3, 'vash')", getFullyQualifiedTableName(tableName2)));
        });

        final ConfiguredAirbyteCatalog configuredCatalog = getConfiguredCatalog();
        configuredCatalog.getStreams().add(CatalogHelpers.createConfiguredAirbyteStream(
                streamName2,
                Field.of("ID", Field.JsonSchemaPrimitive.NUMBER),
                Field.of("NAME", Field.JsonSchemaPrimitive.STRING)));
        configuredCatalog.getStreams().forEach(airbyteStream -> {
            airbyteStream.setSyncMode(SyncMode.INCREMENTAL);
            airbyteStream.setCursorField(Lists.newArrayList("ID"));
        });

        final JdbcState state = new JdbcState().withStreams(Lists.newArrayList(new JdbcStreamState().withStreamName(streamName)));
        final List<AirbyteMessage> actualMessagesFirstSync = MoreIterators.toList(source.read(config, configuredCatalog, Jsons.jsonNode(state)));

        // get last state message.
        final Optional<AirbyteMessage> stateAfterFirstSyncOptional = actualMessagesFirstSync.stream()
                .filter(r -> r.getType() == AirbyteMessage.Type.STATE)
                .reduce((first, second) -> second);
        assertTrue(stateAfterFirstSyncOptional.isPresent());

        // we know the second streams messages are the same as the first minus the updated at column. so we
        // cheat and generate the expected messages off of the first expected messages.
        final List<AirbyteMessage> secondStreamExpectedMessages = getTestMessages()
                .stream()
                .map(Jsons::clone)
                .peek(m -> {
                    m.getRecord().setStream(streamName2);
                    ((ObjectNode) m.getRecord().getData()).remove("UPDATED_AT");
                })
                .collect(Collectors.toList());
        final List<AirbyteMessage> expectedMessagesFirstSync = new ArrayList<>(getTestMessages());
        expectedMessagesFirstSync.add(new AirbyteMessage()
                .withType(AirbyteMessage.Type.STATE)
                .withState(new AirbyteStateMessage()
                        .withData(Jsons.jsonNode(new JdbcState()
                                .withStreams(Lists.newArrayList(
                                        new JdbcStreamState()
                                                .withStreamName(streamName)
                                                .withCursorField(ImmutableList.of("ID"))
                                                .withCursor("3"),
                                        new JdbcStreamState()
                                                .withStreamName(streamName2)
                                                .withCursorField(ImmutableList.of("ID"))))))));
        expectedMessagesFirstSync.addAll(secondStreamExpectedMessages);
        expectedMessagesFirstSync.add(new AirbyteMessage()
                .withType(AirbyteMessage.Type.STATE)
                .withState(new AirbyteStateMessage()
                        .withData(Jsons.jsonNode(new JdbcState()
                                .withStreams(Lists.newArrayList(
                                        new JdbcStreamState()
                                                .withStreamName(streamName)
                                                .withCursorField(ImmutableList.of("ID"))
                                                .withCursor("3"),
                                        new JdbcStreamState()
                                                .withStreamName(streamName2)
                                                .withCursorField(ImmutableList.of("ID"))
                                                .withCursor("3")))))));
        setEmittedAtToNull(actualMessagesFirstSync);

        Assertions.assertEquals(expectedMessagesFirstSync, actualMessagesFirstSync);
    }


    @Override
    public void testDiscoverWithMultipleSchemas() throws Exception {
        // mysql does not have a concept of schemas, so this test does not make sense for it.
        if (getDriverClass().toLowerCase().contains("mysql")) {
            return;
        }

        // add table and data to a separate schema.
        database.execute(connection -> {
            connection.createStatement().execute(
                    String.format("CREATE TABLE %s(id VARCHAR(200), name VARCHAR(200))", JdbcUtils.getFullyQualifiedTableName(SCHEMA_NAME2, TABLE_NAME)));
            connection.createStatement().execute(String.format("INSERT INTO %s(id, name) VALUES (1,'picard')",
                    JdbcUtils.getFullyQualifiedTableName(SCHEMA_NAME2, TABLE_NAME)));
            connection.createStatement().execute(String.format("INSERT INTO %s(id, name) VALUES (2, 'crusher')",
                    JdbcUtils.getFullyQualifiedTableName(SCHEMA_NAME2, TABLE_NAME)));
            connection.createStatement().execute(String.format("INSERT INTO %s(id, name) VALUES (3, 'vash')",
                    JdbcUtils.getFullyQualifiedTableName(SCHEMA_NAME2, TABLE_NAME)));
        });

        final AirbyteCatalog actual = source.discover(config);

        final AirbyteCatalog expected = getCatalog();
        expected.getStreams().add(CatalogHelpers.createAirbyteStream(JdbcUtils.getFullyQualifiedTableName(SCHEMA_NAME2, TABLE_NAME),
                Field.of("id", Field.JsonSchemaPrimitive.STRING),
                Field.of("name", Field.JsonSchemaPrimitive.STRING))
                .withSupportedSyncModes(Lists.newArrayList(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL)));
        // sort streams by name so that we are comparing lists with the same order.
        expected.getStreams().sort(Comparator.comparing(AirbyteStream::getName));
        actual.getStreams().sort(Comparator.comparing(AirbyteStream::getName));
        Assertions.assertEquals(expected, filterOutOtherSchemas(actual));
    }

  @Override
  public boolean supportsSchemas() {
    return true;
  }

  @Override
  public AbstractJdbcSource getSource() {
    return new OracleSource();
  }

  @Override
  public JsonNode getConfig() {
    return config;
  }

  @Override
  public String getDriverClass() {
    return OracleSource.DRIVER_CLASS;
  }

  @AfterAll
  static void cleanUp() {
    ORACLE_DB.close();
  }



  @Override
  public void createSchemas() {
      if (supportsSchemas()) {
          for (String schemaName : TEST_SCHEMAS) {
              try {
                  final String SchemaQuery = String.format("CREATE USER %s IDENTIFIED BY %s DEFAULT TABLESPACE USERS QUOTA UNLIMITED ON USERS", schemaName, schemaName);
                  executeOracleStatement(SchemaQuery);
              } catch (SQLException e) {
                  printSQLException(e);
              }
          }
      }
  }

  public void executeOracleStatement(String query) throws SQLException {
      Connection conn = DriverManager.getConnection(
              ORACLE_DB.getJdbcUrl(),
              ORACLE_DB.getUsername(),
              ORACLE_DB.getPassword()
      );
      try (Statement stmt = conn.createStatement()){
          stmt.execute(query);
      } catch (SQLException e) {
          printSQLException(e);
      }
  }

  public static void printSQLException(SQLException ex) {
        for (Throwable e : ex) {
            if (e instanceof SQLException) {
                if (ignoreSQLException(((SQLException)e).getSQLState()) == false) {
                    e.printStackTrace(System.err);
                    System.err.println("SQLState: " + ((SQLException)e).getSQLState());
                    System.err.println("Error Code: " + ((SQLException)e).getErrorCode());
                    System.err.println("Message: " + e.getMessage());
                    Throwable t = ex.getCause();
                    while (t != null) {
                        System.out.println("Cause: " + t);
                        t = t.getCause();
                    }
                }
            }
        }
    }

    public static boolean ignoreSQLException(String sqlState) {
        if (sqlState == null) {
            System.out.println("The SQL state is not defined!");
            return false;
        }
        // X0Y32: Jar file already exists in schema
        if (sqlState.equalsIgnoreCase("X0Y32"))
            return true;
        // 42Y55: Table already exists in schema
        if (sqlState.equalsIgnoreCase("42Y55"))
            return true;
        // 42000: User name already exists
        if (sqlState.equalsIgnoreCase("42000"))
            return true;

        return false;
    }
}
