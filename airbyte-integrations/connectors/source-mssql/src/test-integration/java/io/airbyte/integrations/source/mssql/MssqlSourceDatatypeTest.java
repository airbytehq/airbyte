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

package io.airbyte.integrations.source.mssql;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.string.Strings;
import io.airbyte.db.Database;
import io.airbyte.db.Databases;
import io.airbyte.integrations.standardtest.source.AbstractSourceDatabaseTypeTest;
import io.airbyte.integrations.standardtest.source.TestDataHolder;
import io.airbyte.integrations.standardtest.source.TestDestinationEnv;
import io.airbyte.protocol.models.JsonSchemaPrimitive;
import org.testcontainers.containers.MSSQLServerContainer;

public class MssqlSourceDatatypeTest extends AbstractSourceDatabaseTypeTest {

  static final String DB_NAME = Strings.addRandomSuffix("db", "_", 10).toLowerCase();
  protected static MSSQLServerContainer<?> container;
  protected JsonNode config;

  @Override
  protected Database setupDatabase() throws Exception {
    container = new MSSQLServerContainer<>("mcr.microsoft.com/mssql/server:2019-latest")
        .acceptLicense();
    container.start();

    final JsonNode configWithoutDbName = Jsons.jsonNode(ImmutableMap.builder()
        .put("host", container.getHost())
        .put("port", container.getFirstMappedPort())
        .put("username", container.getUsername())
        .put("password", container.getPassword())
        .build());

    final Database database = getDatabase(configWithoutDbName);
    database.query(ctx -> {
      ctx.fetch(String.format("CREATE DATABASE %s;", DB_NAME));
      ctx.fetch(String.format("USE %s;", DB_NAME));
      return null;
    });

    config = Jsons.clone(configWithoutDbName);
    ((ObjectNode) config).put("database", DB_NAME);

    return database;
  }

  private static Database getDatabase(JsonNode config) {
    return Databases.createDatabase(
        config.get("username").asText(),
        config.get("password").asText(),
        String.format("jdbc:sqlserver://%s:%s",
            config.get("host").asText(),
            config.get("port").asInt()),
        "com.microsoft.sqlserver.jdbc.SQLServerDriver",
        null);
  }

  @Override
  protected String getNameSpace() {
    return "dbo";
  }

  @Override
  protected String getImageName() {
    return "airbyte/source-mssql:dev";
  }

  @Override
  protected JsonNode getConfig() {
    return config;
  }

  @Override
  protected void tearDown(TestDestinationEnv testEnv) throws Exception {
    container.stop();
    container.close();
  }

  @Override
  protected void initTests() {
    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("bigint")
            .airbyteType(JsonSchemaPrimitive.NUMBER)
            .addInsertValues("-9223372036854775808", "9223372036854775807", "0", "null")
            .addExpectedValues("-9223372036854775808", "9223372036854775807", "0", null)
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("int")
            .airbyteType(JsonSchemaPrimitive.NUMBER)
            .addInsertValues("null", "-2147483648", "2147483647")
            .addExpectedValues(null, "-2147483648", "2147483647")
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("smallint")
            .airbyteType(JsonSchemaPrimitive.NUMBER)
            .addInsertValues("null", "-32768", "32767")
            .addExpectedValues(null, "-32768", "32767")
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("tinyint")
            .airbyteType(JsonSchemaPrimitive.NUMBER)
            .addInsertValues("null", "0", "255")
            .addExpectedValues(null, "0", "255")
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("bit")
            .airbyteType(JsonSchemaPrimitive.NUMBER)
            .addInsertValues("null", "0", "1", "'true'", "'false'")
            .addExpectedValues(null, "false", "true", "true", "false")
            .addInsertValues("null")
            .addNullExpectedValue()
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("decimal")
            .fullSourceDataType("DECIMAL(5,2)")
            .airbyteType(JsonSchemaPrimitive.NUMBER)
            .addInsertValues("999", "5.1", "0", "null")
            .addExpectedValues("999", "5.1", "0", null)
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("numeric")
            .airbyteType(JsonSchemaPrimitive.NUMBER)
            .addInsertValues("'99999'", "null")
            .addExpectedValues("99999", null)
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("money")
            .airbyteType(JsonSchemaPrimitive.NUMBER)
            .addInsertValues("null", "'9990000.99'")
            .addExpectedValues(null, "9990000.99")
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("smallmoney")
            .airbyteType(JsonSchemaPrimitive.NUMBER)
            .addInsertValues("null", "'-214748.3648'", "214748.3647")
            .addExpectedValues(null, "-214748.3648", "214748.3647")
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("float")
            .airbyteType(JsonSchemaPrimitive.NUMBER)
            .addInsertValues("'123'", "'1234567890.1234567'", "null")
            .addExpectedValues("123.0", "1.2345678901234567E9", null)
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("real")
            .airbyteType(JsonSchemaPrimitive.NUMBER)
            .addInsertValues("'123'", "'1234567890.1234567'", "null")
            .addExpectedValues("123.0", "1.23456794E9", null)
            .build());

    // TODO JdbcUtils-> DATE_FORMAT is set as ""yyyy-MM-dd'T'HH:mm:ss'Z'"" so dates would be
    // always represented as a datetime with 00:00:00 time
    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("date")
            .airbyteType(JsonSchemaPrimitive.STRING)
            .addInsertValues("'0001-01-01'", "'9999-12-31'", "'1999-01-08'",
                "null")
            .addExpectedValues("0001-01-01T00:00:00Z", "9999-12-31T00:00:00Z",
                "1999-01-08T00:00:00Z", null)
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("smalldatetime")
            .airbyteType(JsonSchemaPrimitive.STRING)
            .addInsertValues("'1900-01-01'", "'2079-06-06'", "null")
            .addExpectedValues("1900-01-01T00:00:00Z", "2079-06-06T00:00:00Z", null)
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("datetime")
            .airbyteType(JsonSchemaPrimitive.STRING)
            .addInsertValues("'1753-01-01'", "'9999-12-31'", "null")
            .addExpectedValues("1753-01-01T00:00:00Z", "9999-12-31T00:00:00Z", null)
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("datetime2")
            .airbyteType(JsonSchemaPrimitive.STRING)
            .addInsertValues("'0001-01-01'", "'9999-12-31'", "null")
            .addExpectedValues("0001-01-01T00:00:00Z", "9999-12-31T00:00:00Z", null)
            .build());

    // TODO JdbcUtils-> DATE_FORMAT is set as ""yyyy-MM-dd'T'HH:mm:ss'Z'"" for both Date and Time types.
    // So Time only (04:05:06) would be represented like "1970-01-01T04:05:06Z" which is incorrect
    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("time")
            .airbyteType(JsonSchemaPrimitive.STRING)
            .addInsertValues("null")
            .addNullExpectedValue()
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("datetimeoffset")
            .airbyteType(JsonSchemaPrimitive.STRING)
            .addInsertValues("'0001-01-10 00:00:00 +01:00'", "'9999-01-10 00:00:00 +01:00'", "null")
            .addExpectedValues("0001-01-10 00:00:00.0000000 +01:00",
                "9999-01-10 00:00:00.0000000 +01:00", null)
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("char")
            .airbyteType(JsonSchemaPrimitive.STRING)
            .addInsertValues("'a'", "'*'", "null")
            .addExpectedValues("a", "*", null)
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("varchar")
            .fullSourceDataType("varchar(max) COLLATE Latin1_General_100_CI_AI_SC_UTF8")
            .airbyteType(JsonSchemaPrimitive.STRING)
            .addInsertValues("'a'", "'abc'", "N'Миші йдуть на південь, не питай чому;'", "N'櫻花分店'",
                "''", "null", "N'\\xF0\\x9F\\x9A\\x80'")
            .addExpectedValues("a", "abc", "Миші йдуть на південь, не питай чому;", "櫻花分店", "",
                null, "\\xF0\\x9F\\x9A\\x80")
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("text")
            .airbyteType(JsonSchemaPrimitive.STRING)
            .addInsertValues("'a'", "'abc'", "'Some test text 123$%^&*()_'", "''", "null")
            .addExpectedValues("a", "abc", "Some test text 123$%^&*()_", "", null)
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("nchar")
            .airbyteType(JsonSchemaPrimitive.STRING)
            .addInsertValues("'a'", "'*'", "N'ї'", "null")
            .addExpectedValues("a", "*", "ї", null)
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("nvarchar")
            .fullSourceDataType("nvarchar(max)")
            .airbyteType(JsonSchemaPrimitive.STRING)
            .addInsertValues("'a'", "'abc'", "N'Миші йдуть на південь, не питай чому;'", "N'櫻花分店'",
                "''", "null", "N'\\xF0\\x9F\\x9A\\x80'")
            .addExpectedValues("a", "abc", "Миші йдуть на південь, не питай чому;", "櫻花分店", "",
                null, "\\xF0\\x9F\\x9A\\x80")
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("ntext")
            .airbyteType(JsonSchemaPrimitive.STRING)
            .addInsertValues("'a'", "'abc'", "N'Миші йдуть на південь, не питай чому;'", "N'櫻花分店'",
                "''", "null", "N'\\xF0\\x9F\\x9A\\x80'")
            .addExpectedValues("a", "abc", "Миші йдуть на південь, не питай чому;", "櫻花分店", "",
                null, "\\xF0\\x9F\\x9A\\x80")
            .build());

    // TODO BUG Returns binary value instead of actual value
    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("binary")
            .airbyteType(JsonSchemaPrimitive.STRING)
            // .addInsertValues("CAST( 'A' AS VARBINARY)", "null")
            // .addExpectedValues("A")
            .addInsertValues("null")
            .addNullExpectedValue()
            .build());

    // TODO BUG Returns binary value instead of actual value
    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("varbinary")
            .fullSourceDataType("varbinary(30)")
            .airbyteType(JsonSchemaPrimitive.STRING)
            // .addInsertValues("CAST( 'ABC' AS VARBINARY)", "null")
            // .addExpectedValues("A")
            .addInsertValues("null")
            .addNullExpectedValue()
            .build());

    // TODO BUG: airbyte returns binary representation instead of readable one
    // create table dbo_1_hierarchyid1 (test_column hierarchyid);
    // insert dbo_1_hierarchyid1 values ('/1/1/');
    // select test_column ,test_column.ToString() AS [Node Text],test_column.GetLevel() [Node Level]
    // from dbo_1_hierarchyid1;
    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("hierarchyid")
            .airbyteType(JsonSchemaPrimitive.STRING)
            .addInsertValues("null")
            .addNullExpectedValue()
            // .addInsertValues("null","'/1/1/'")
            // .addExpectedValues(null, "/1/1/")
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("sql_variant")
            .airbyteType(JsonSchemaPrimitive.STRING)
            .addInsertValues("'a'", "'abc'", "N'Миші йдуть на південь, не питай чому;'", "N'櫻花分店'",
                "''", "null", "N'\\xF0\\x9F\\x9A\\x80'")
            .addExpectedValues("a", "abc", "Миші йдуть на південь, не питай чому;", "櫻花分店", "",
                null, "\\xF0\\x9F\\x9A\\x80")
            .build());

    // TODO BUG: Airbyte returns binary representation instead of text one.
    // Proper select query example: SELECT test_column.STAsText() from dbo_1_geometry;
    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("geometry")
            .airbyteType(JsonSchemaPrimitive.STRING)
            .addInsertValues("null")
            .addNullExpectedValue()
            // .addInsertValues("geometry::STGeomFromText('LINESTRING (100 100, 20 180, 180 180)', 0)")
            // .addExpectedValues("LINESTRING (100 100, 20 180, 180 180)",
            // "POLYGON ((0 0, 150 0, 150 150, 0 150, 0 0)", null)
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("uniqueidentifier")
            .airbyteType(JsonSchemaPrimitive.STRING)
            .addInsertValues("'375CFC44-CAE3-4E43-8083-821D2DF0E626'", "null")
            .addExpectedValues("375CFC44-CAE3-4E43-8083-821D2DF0E626", null)
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("xml")
            .airbyteType(JsonSchemaPrimitive.STRING)
            .addInsertValues(
                "'<user><user_id>1</user_id></user>'", "null", "''")
            .addExpectedValues("<user><user_id>1</user_id></user>", null, "")
            .build());

    // TODO BUG: Airbyte returns binary representation instead of text one.
    // Proper select query example: SELECT test_column.STAsText() from dbo_1_geography;
    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("geography")
            .airbyteType(JsonSchemaPrimitive.STRING)
            .addInsertValues("null")
            .addNullExpectedValue()
            // .addInsertValues("geography::STGeomFromText('LINESTRING(-122.360 47.656, -122.343 47.656 )',
            // 4326)")
            // .addExpectedValues("LINESTRING(-122.360 47.656, -122.343 47.656 )", null)
            .build());

  }

}
