/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.jdbc;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ArrayNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.base.Charsets;
import com.google.common.collect.ImmutableMap;
import com.google.common.collect.Lists;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.stream.MoreStreams;
import io.airbyte.commons.string.Strings;
import io.airbyte.db.factory.DataSourceFactory;
import io.airbyte.db.factory.DatabaseDriver;
import io.airbyte.protocol.models.JsonSchemaType;
import io.airbyte.test.utils.PostgreSQLContainerHelper;
import java.math.BigDecimal;
import java.sql.Connection;
import java.sql.JDBCType;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;
import javax.sql.DataSource;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.testcontainers.containers.PostgreSQLContainer;
import org.testcontainers.utility.MountableFile;

@SuppressWarnings("PMD.CheckResultSet")
class TestJdbcUtils {

  private String dbName;
  private static final String ONE_POINT_0 = "1.0,";

  private static final List<JsonNode> RECORDS_AS_JSON = Lists.newArrayList(
      Jsons.jsonNode(ImmutableMap.of("id", 1, "name", "picard")),
      Jsons.jsonNode(ImmutableMap.of("id", 2, "name", "crusher")),
      Jsons.jsonNode(ImmutableMap.of("id", 3, "name", "vash")));

  private static PostgreSQLContainer<?> PSQL_DB;

  private DataSource dataSource;
  private static final JdbcSourceOperations sourceOperations = JdbcUtils.getDefaultSourceOperations();

  @BeforeAll
  static void init() {
    PSQL_DB = new PostgreSQLContainer<>("postgres:13-alpine");
    PSQL_DB.start();

  }

  @BeforeEach
  void setup() throws Exception {
    dbName = Strings.addRandomSuffix("db", "_", 10);

    final JsonNode config = getConfig(PSQL_DB, dbName);

    final String initScriptName = "init_" + dbName.concat(".sql");
    final String tmpFilePath = IOs.writeFileToRandomTmpDir(initScriptName, "CREATE DATABASE " + dbName + ";");
    PostgreSQLContainerHelper.runSqlScript(MountableFile.forHostPath(tmpFilePath), PSQL_DB);

    dataSource = DataSourceFactory.create(
        config.get(JdbcUtils.USERNAME_KEY).asText(),
        config.get(JdbcUtils.PASSWORD_KEY).asText(),
        DatabaseDriver.POSTGRESQL.getDriverClassName(),
        String.format(DatabaseDriver.POSTGRESQL.getUrlFormatString(),
            config.get(JdbcUtils.HOST_KEY).asText(),
            config.get(JdbcUtils.PORT_KEY).asInt(),
            config.get(JdbcUtils.DATABASE_KEY).asText()));

    final JdbcDatabase defaultJdbcDatabase = new DefaultJdbcDatabase(dataSource);

    defaultJdbcDatabase.execute(connection -> {
      connection.createStatement().execute("CREATE TABLE id_and_name(id INTEGER, name VARCHAR(200));");
      connection.createStatement().execute("INSERT INTO id_and_name (id, name) VALUES (1,'picard'),  (2, 'crusher'), (3, 'vash');");
    });
  }

  private JsonNode getConfig(final PostgreSQLContainer<?> psqlDb, final String dbName) {
    return Jsons.jsonNode(ImmutableMap.builder()
        .put(JdbcUtils.HOST_KEY, psqlDb.getHost())
        .put(JdbcUtils.PORT_KEY, psqlDb.getFirstMappedPort())
        .put(JdbcUtils.DATABASE_KEY, dbName)
        .put(JdbcUtils.USERNAME_KEY, psqlDb.getUsername())
        .put(JdbcUtils.PASSWORD_KEY, psqlDb.getPassword())
        .build());
  }

  // Takes in a generic sslValue because useSsl maps sslValue to a boolean
  private <T> JsonNode getConfigWithSsl(final PostgreSQLContainer<?> psqlDb, final String dbName, final T sslValue) {
    return Jsons.jsonNode(ImmutableMap.builder()
        .put("host", psqlDb.getHost())
        .put("port", psqlDb.getFirstMappedPort())
        .put("database", dbName)
        .put("username", psqlDb.getUsername())
        .put("password", psqlDb.getPassword())
        .put("ssl", sslValue)
        .build());
  }

  @Test
  void testRowToJson() throws SQLException {
    try (final Connection connection = dataSource.getConnection()) {
      final ResultSet rs = connection.createStatement().executeQuery("SELECT * FROM id_and_name;");
      rs.next();
      assertEquals(RECORDS_AS_JSON.get(0), sourceOperations.rowToJson(rs));
    }
  }

  @Test
  void testToStream() throws SQLException {
    try (final Connection connection = dataSource.getConnection()) {
      final ResultSet rs = connection.createStatement().executeQuery("SELECT * FROM id_and_name;");
      final List<JsonNode> actual = JdbcDatabase.toUnsafeStream(rs, sourceOperations::rowToJson).collect(Collectors.toList());
      assertEquals(RECORDS_AS_JSON, actual);
    }
  }

  // test conversion of every JDBCType that we support to Json.
  @Test
  void testSetJsonField() throws SQLException {
    try (final Connection connection = dataSource.getConnection()) {
      createTableWithAllTypes(connection);
      insertRecordOfEachType(connection);
      assertExpectedOutputValues(connection, jsonFieldExpectedValues());
      assertExpectedOutputTypes(connection);
    }
  }

  // test setting on a PreparedStatement every JDBCType that we support.
  @Test
  void testSetStatementField() throws SQLException {
    try (final Connection connection = dataSource.getConnection()) {
      createTableWithAllTypes(connection);

      final PreparedStatement ps = connection.prepareStatement("INSERT INTO data VALUES(?::bit,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?);");

      // insert the bit here to stay consistent even though setStatementField does not support it yet.
      ps.setString(1, "1");
      sourceOperations.setStatementField(ps, 2, JDBCType.BOOLEAN, "true");
      sourceOperations.setStatementField(ps, 3, JDBCType.SMALLINT, "1");
      sourceOperations.setStatementField(ps, 4, JDBCType.INTEGER, "1");
      sourceOperations.setStatementField(ps, 5, JDBCType.BIGINT, "1");
      sourceOperations.setStatementField(ps, 6, JDBCType.FLOAT, "1.0");
      sourceOperations.setStatementField(ps, 7, JDBCType.DOUBLE, "1.0");
      sourceOperations.setStatementField(ps, 8, JDBCType.REAL, "1.0");
      sourceOperations.setStatementField(ps, 9, JDBCType.NUMERIC, "1");
      sourceOperations.setStatementField(ps, 10, JDBCType.DECIMAL, "1");
      sourceOperations.setStatementField(ps, 11, JDBCType.CHAR, "a");
      sourceOperations.setStatementField(ps, 12, JDBCType.VARCHAR, "a");
      sourceOperations.setStatementField(ps, 13, JDBCType.DATE, "2020-11-01T00:00:00Z");
      sourceOperations.setStatementField(ps, 14, JDBCType.TIME, "1970-01-01T05:00:00.000Z");
      sourceOperations.setStatementField(ps, 15, JDBCType.TIMESTAMP, "2001-09-29T03:00:00.000Z");
      sourceOperations.setStatementField(ps, 16, JDBCType.BINARY, "61616161");

      ps.execute();

      assertExpectedOutputValues(connection, expectedValues());
      assertExpectedOutputTypes(connection);
    }
  }

  @Test
  void testUseSslWithSslNotSet() {
    final JsonNode config = getConfig(PSQL_DB, dbName);
    final boolean sslSet = JdbcUtils.useSsl(config);
    assertTrue(sslSet);
  }

  @Test
  void testUseSslWithSslSetAndValueStringFalse() {
    final JsonNode config = getConfigWithSsl(PSQL_DB, dbName, "false");
    final boolean sslSet = JdbcUtils.useSsl(config);
    assertFalse(sslSet);
  }

  @Test
  void testUseSslWithSslSetAndValueIntegerFalse() {
    final JsonNode config = getConfigWithSsl(PSQL_DB, dbName, 0);
    final boolean sslSet = JdbcUtils.useSsl(config);
    assertFalse(sslSet);
  }

  @Test
  void testUseSslWithSslSetAndValueStringTrue() {
    final JsonNode config = getConfigWithSsl(PSQL_DB, dbName, "true");
    final boolean sslSet = JdbcUtils.useSsl(config);
    assertTrue(sslSet);
  }

  @Test
  void testUssSslWithSslSetAndValueIntegerTrue() {
    final JsonNode config = getConfigWithSsl(PSQL_DB, dbName, 3);
    final boolean sslSet = JdbcUtils.useSsl(config);
    assertTrue(sslSet);
  }

  private static void createTableWithAllTypes(final Connection connection) throws SQLException {
    // jdbctype not included because they are not directly supported in postgres: TINYINT, LONGVARCHAR,
    // VARBINAR, LONGVARBINARY
    connection.createStatement().execute("CREATE TABLE data("
        + "bit BIT, "
        + "boolean BOOLEAN, "
        + "smallint SMALLINT,"
        + "int INTEGER,"
        + "bigint BIGINT,"
        + "float FLOAT,"
        + "double DOUBLE PRECISION,"
        + "real REAL,"
        + "numeric NUMERIC,"
        + "decimal DECIMAL,"
        + "char CHAR,"
        + "varchar VARCHAR,"
        + "date DATE,"
        + "time TIME,"
        + "timestamp TIMESTAMP,"
        + "binary1 bytea,"
        + "text_array _text,"
        + "int_array int[]"
        + ");");

  }

  private static void insertRecordOfEachType(final Connection connection) throws SQLException {
    connection.createStatement().execute("INSERT INTO data("
        + "bit,"
        + "boolean,"
        + "smallint,"
        + "int,"
        + "bigint,"
        + "float,"
        + "double,"
        + "real,"
        + "numeric,"
        + "decimal,"
        + "char,"
        + "varchar,"
        + "date,"
        + "time,"
        + "timestamp,"
        + "binary1,"
        + "text_array,"
        + "int_array"
        + ") VALUES("
        + "1::bit(1),"
        + "true,"
        + "1,"
        + "1,"
        + "1,"
        + ONE_POINT_0
        + ONE_POINT_0
        + ONE_POINT_0
        + "1,"
        + ONE_POINT_0
        + "'a',"
        + "'a',"
        + "'2020-11-01',"
        + "'05:00',"
        + "'2001-09-29 03:00',"
        + "decode('61616161', 'hex'),"
        + "'{one,two,three}',"
        + "'{1,2,3}'"
        + ");");
  }

  private static void assertExpectedOutputValues(final Connection connection, final ObjectNode expected) throws SQLException {
    final ResultSet resultSet = connection.createStatement().executeQuery("SELECT * FROM data;");

    resultSet.next();
    final JsonNode actual = sourceOperations.rowToJson(resultSet);

    // field-wise comparison to make debugging easier.
    MoreStreams.toStream(expected.fields()).forEach(e -> assertEquals(e.getValue(), actual.get(e.getKey()), "key: " + e.getKey()));
    assertEquals(expected, actual);
  }

  private static void assertExpectedOutputTypes(final Connection connection) throws SQLException {
    final ResultSet resultSet = connection.createStatement().executeQuery("SELECT * FROM data;");

    resultSet.next();
    final int columnCount = resultSet.getMetaData().getColumnCount();
    final Map<String, JsonSchemaType> actual = new HashMap<>(columnCount);
    for (int i = 1; i <= columnCount; i++) {
      actual.put(resultSet.getMetaData().getColumnName(i), sourceOperations.getJsonType(JDBCType.valueOf(resultSet.getMetaData().getColumnType(i))));
    }

    final Map<String, JsonSchemaType> expected = ImmutableMap.<String, JsonSchemaType>builder()
        .put("bit", JsonSchemaType.BOOLEAN)
        .put("boolean", JsonSchemaType.BOOLEAN)
        .put("smallint", JsonSchemaType.INTEGER)
        .put("int", JsonSchemaType.INTEGER)
        .put("bigint", JsonSchemaType.INTEGER)
        .put("float", JsonSchemaType.NUMBER)
        .put("double", JsonSchemaType.NUMBER)
        .put("real", JsonSchemaType.NUMBER)
        .put("numeric", JsonSchemaType.NUMBER)
        .put("decimal", JsonSchemaType.NUMBER)
        .put("char", JsonSchemaType.STRING)
        .put("varchar", JsonSchemaType.STRING)
        .put("date", JsonSchemaType.STRING)
        .put("time", JsonSchemaType.STRING)
        .put("timestamp", JsonSchemaType.STRING)
        .put("binary1", JsonSchemaType.STRING_BASE_64)
        .put("text_array", JsonSchemaType.ARRAY)
        .put("int_array", JsonSchemaType.ARRAY)
        .build();

    assertEquals(actual, expected);
  }

  private ObjectNode jsonFieldExpectedValues() {
    final ObjectNode expected = expectedValues();
    final ArrayNode arrayNode = new ObjectMapper().createArrayNode();
    arrayNode.add("one");
    arrayNode.add("two");
    arrayNode.add("three");
    expected.set("text_array", arrayNode);

    final ArrayNode arrayNode2 = new ObjectMapper().createArrayNode();
    arrayNode2.add("1");
    arrayNode2.add("2");
    arrayNode2.add("3");
    expected.set("int_array", arrayNode2);

    return expected;
  }

  private ObjectNode expectedValues() {
    final ObjectNode expected = (ObjectNode) Jsons.jsonNode(Collections.emptyMap());
    expected.put("bit", true);
    expected.put("boolean", true);
    expected.put("smallint", (short) 1);
    expected.put("int", 1);
    expected.put("bigint", (long) 1);
    expected.put("float", (double) 1.0);
    expected.put("double", (double) 1.0);
    expected.put("real", (float) 1.0);
    expected.put("numeric", new BigDecimal(1));
    expected.put("decimal", new BigDecimal(1));
    expected.put("char", "a");
    expected.put("varchar", "a");
    // todo (cgardens) we should parse this to a date string
    expected.put("date", "2020-11-01T00:00:00Z");
    // todo (cgardens) we should parse this to a time string
    expected.put("time", "1970-01-01T05:00:00Z");
    expected.put("timestamp", "2001-09-29T03:00:00.000000Z");
    expected.put("binary1", "aaaa".getBytes(Charsets.UTF_8));
    return expected;
  }

}
