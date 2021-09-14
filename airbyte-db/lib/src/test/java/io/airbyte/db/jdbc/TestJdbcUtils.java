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

package io.airbyte.db.jdbc;

import static org.junit.jupiter.api.Assertions.assertEquals;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.base.Charsets;
import com.google.common.collect.ImmutableMap;
import com.google.common.collect.Lists;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.stream.MoreStreams;
import io.airbyte.commons.string.Strings;
import io.airbyte.protocol.models.JsonSchemaPrimitive;
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
import org.apache.commons.dbcp2.BasicDataSource;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.testcontainers.containers.PostgreSQLContainer;
import org.testcontainers.utility.MountableFile;

public class TestJdbcUtils {

  private static final List<JsonNode> RECORDS_AS_JSON = Lists.newArrayList(
      Jsons.jsonNode(ImmutableMap.of("id", 1, "name", "picard")),
      Jsons.jsonNode(ImmutableMap.of("id", 2, "name", "crusher")),
      Jsons.jsonNode(ImmutableMap.of("id", 3, "name", "vash")));

  private static PostgreSQLContainer<?> PSQL_DB;

  private BasicDataSource dataSource;
  private static final JdbcSourceOperations sourceOperations = JdbcUtils.getDefaultSourceOperations();

  @BeforeAll
  static void init() {
    PSQL_DB = new PostgreSQLContainer<>("postgres:13-alpine");
    PSQL_DB.start();

  }

  @BeforeEach
  void setup() throws Exception {
    final String dbName = Strings.addRandomSuffix("db", "_", 10);

    final JsonNode config = getConfig(PSQL_DB, dbName);

    final String initScriptName = "init_" + dbName.concat(".sql");
    final String tmpFilePath = IOs.writeFileToRandomTmpDir(initScriptName, "CREATE DATABASE " + dbName + ";");
    PostgreSQLContainerHelper.runSqlScript(MountableFile.forHostPath(tmpFilePath), PSQL_DB);

    dataSource = new BasicDataSource();
    dataSource.setDriverClassName("org.postgresql.Driver");
    dataSource.setUsername(config.get("username").asText());
    dataSource.setPassword(config.get("password").asText());
    dataSource.setUrl(String.format("jdbc:postgresql://%s:%s/%s",
        config.get("host").asText(),
        config.get("port").asText(),
        config.get("database").asText()));

    final JdbcDatabase defaultJdbcDatabase = new DefaultJdbcDatabase(dataSource);

    defaultJdbcDatabase.execute(connection -> {
      connection.createStatement().execute("CREATE TABLE id_and_name(id INTEGER, name VARCHAR(200));");
      connection.createStatement().execute("INSERT INTO id_and_name (id, name) VALUES (1,'picard'),  (2, 'crusher'), (3, 'vash');");
    });
  }

  private JsonNode getConfig(PostgreSQLContainer<?> psqlDb, String dbName) {
    return Jsons.jsonNode(ImmutableMap.builder()
        .put("host", psqlDb.getHost())
        .put("port", psqlDb.getFirstMappedPort())
        .put("database", dbName)
        .put("username", psqlDb.getUsername())
        .put("password", psqlDb.getPassword())
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
      final List<JsonNode> actual = sourceOperations.toStream(rs, sourceOperations::rowToJson).collect(Collectors.toList());
      assertEquals(RECORDS_AS_JSON, actual);
    }
  }

  // test conversion of every JDBCType that we support to Json.
  @Test
  void testSetJsonField() throws SQLException {
    try (final Connection connection = dataSource.getConnection()) {
      createTableWithAllTypes(connection);
      insertRecordOfEachType(connection);
      assertExpectedOutputValues(connection);
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
      sourceOperations.setStatementField(ps, 14, JDBCType.TIME, "1970-01-01T05:00:00Z");
      sourceOperations.setStatementField(ps, 15, JDBCType.TIMESTAMP, "2001-09-29T03:00:00Z");
      sourceOperations.setStatementField(ps, 16, JDBCType.BINARY, "61616161");

      ps.execute();

      assertExpectedOutputValues(connection);
      assertExpectedOutputTypes(connection);
    }
  }

  private static void createTableWithAllTypes(Connection connection) throws SQLException {
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
        + "binary1 bytea"
        + ");");

  }

  private static void insertRecordOfEachType(Connection connection) throws SQLException {
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
        + "binary1"
        + ") VALUES("
        + "1::bit(1),"
        + "true,"
        + "1,"
        + "1,"
        + "1,"
        + "1.0,"
        + "1.0,"
        + "1.0,"
        + "1,"
        + "1.0,"
        + "'a',"
        + "'a',"
        + "'2020-11-01',"
        + "'05:00',"
        + "'2001-09-29 03:00',"
        + "decode('61616161', 'hex')"
        + ");");
  }

  private static void assertExpectedOutputValues(Connection connection) throws SQLException {
    final ResultSet resultSet = connection.createStatement().executeQuery("SELECT * FROM data;");

    resultSet.next();
    final JsonNode actual = sourceOperations.rowToJson(resultSet);

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
    expected.put("timestamp", "2001-09-29T03:00:00Z");
    expected.put("binary1", "aaaa".getBytes(Charsets.UTF_8));

    // field-wise comparison to make debugging easier.
    MoreStreams.toStream(expected.fields()).forEach(e -> assertEquals(e.getValue(), actual.get(e.getKey()), "key: " + e.getKey()));
    assertEquals(expected, actual);
  }

  private static void assertExpectedOutputTypes(Connection connection) throws SQLException {
    final ResultSet resultSet = connection.createStatement().executeQuery("SELECT * FROM data;");

    resultSet.next();
    final int columnCount = resultSet.getMetaData().getColumnCount();
    final Map<String, JsonSchemaPrimitive> actual = new HashMap<>(columnCount);
    for (int i = 1; i <= columnCount; i++) {
      actual.put(resultSet.getMetaData().getColumnName(i), sourceOperations.getType(JDBCType.valueOf(resultSet.getMetaData().getColumnType(i))));
    }

    final Map<String, JsonSchemaPrimitive> expected = ImmutableMap.<String, JsonSchemaPrimitive>builder()
        .put("bit", JsonSchemaPrimitive.BOOLEAN)
        .put("boolean", JsonSchemaPrimitive.BOOLEAN)
        .put("smallint", JsonSchemaPrimitive.NUMBER)
        .put("int", JsonSchemaPrimitive.NUMBER)
        .put("bigint", JsonSchemaPrimitive.NUMBER)
        .put("float", JsonSchemaPrimitive.NUMBER)
        .put("double", JsonSchemaPrimitive.NUMBER)
        .put("real", JsonSchemaPrimitive.NUMBER)
        .put("numeric", JsonSchemaPrimitive.NUMBER)
        .put("decimal", JsonSchemaPrimitive.NUMBER)
        .put("char", JsonSchemaPrimitive.STRING)
        .put("varchar", JsonSchemaPrimitive.STRING)
        .put("date", JsonSchemaPrimitive.STRING)
        .put("time", JsonSchemaPrimitive.STRING)
        .put("timestamp", JsonSchemaPrimitive.STRING)
        .put("binary1", JsonSchemaPrimitive.STRING)
        .build();

    assertEquals(actual, expected);
  }

}
