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

package io.airbyte.integrations.io.airbyte.integration_tests.sources;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.Database;
import io.airbyte.db.Databases;
import io.airbyte.integrations.source.snowflake.SnowflakeSource;
import io.airbyte.integrations.standardtest.source.AbstractSourceDatabaseTypeTest;
import io.airbyte.integrations.standardtest.source.TestDataHolder;
import io.airbyte.integrations.standardtest.source.TestDestinationEnv;
import io.airbyte.protocol.models.JsonSchemaPrimitive;
import java.nio.file.Path;
import org.jooq.SQLDialect;

public class SnowflakeSourceDatatypeTest extends AbstractSourceDatabaseTypeTest {

  private static final String SCHEMA_NAME = "TEST";
  private static final String INSERT_SEMI_STRUCTURED_SQL = "INSERT INTO %1$s (ID, TEST_COLUMN) SELECT %2$s, %3$s";

  private JsonNode config;
  private Database database;

  @Override
  protected String getImageName() {
    return "airbyte/source-snowflake:dev";
  }

  @Override
  protected JsonNode getConfig() throws Exception {
    return config;
  }

  @Override
  protected Database setupDatabase() throws Exception {
    config = Jsons.deserialize(IOs.readFile(Path.of("secrets/config.json")));

    database = getDatabase();

    final String createSchemaQuery = String.format("CREATE SCHEMA %s", SCHEMA_NAME);
    database.query(ctx -> ctx.fetch(createSchemaQuery));
    return database;
  }

  private Database getDatabase() {
    return Databases.createDatabase(
        config.get("username").asText(),
        config.get("password").asText(),
        String.format("jdbc:snowflake://%s/",
            config.get("host").asText()),
        SnowflakeSource.DRIVER_CLASS,
        SQLDialect.DEFAULT,
        String.format("role=%s;warehouse=%s;database=%s",
            config.get("role").asText(),
            config.get("warehouse").asText(),
            config.get("database").asText()));
  }

  @Override
  protected void tearDown(TestDestinationEnv testEnv) throws Exception {
    final String dropSchemaQuery = String
        .format("DROP SCHEMA IF EXISTS %s", SCHEMA_NAME);
    database = getDatabase();
    database.query(ctx -> ctx.fetch(dropSchemaQuery));
    database.close();
  }

  @Override
  protected String getNameSpace() {
    return SCHEMA_NAME;
  }

  @Override
  protected String getIdColumnName() {
    return "ID";
  }

  @Override
  protected String getTestColumnName() {
    return "TEST_COLUMN";
  }

  @Override
  protected void initTests() {
    // TODO https://github.com/airbytehq/airbyte/issues/4316
    // should be tested with Snowflake extreme range -99999999999999999999999999999999999999 to
    // +99999999999999999999999999999999999999 (inclusive)
    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("NUMBER")
            .airbyteType(JsonSchemaPrimitive.NUMBER)
            .addInsertValues("null", "9223372036854775807", "-9223372036854775808")
            .addExpectedValues(null, "9223372036854775807", "-9223372036854775808")
            .build());
    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("DECIMAL")
            .airbyteType(JsonSchemaPrimitive.NUMBER)
            .addInsertValues("null", "9223372036854775807", "-9223372036854775808")
            .addExpectedValues(null, "9223372036854775807", "-9223372036854775808")
            .build());
    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("NUMERIC")
            .airbyteType(JsonSchemaPrimitive.NUMBER)
            .addInsertValues("null", "9223372036854775807", "-9223372036854775808")
            .addExpectedValues(null, "9223372036854775807", "-9223372036854775808")
            .build());
    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("BIGINT")
            .airbyteType(JsonSchemaPrimitive.NUMBER)
            .addInsertValues("null", "9223372036854775807", "-9223372036854775808")
            .addExpectedValues(null, "9223372036854775807", "-9223372036854775808")
            .build());
    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("INT")
            .airbyteType(JsonSchemaPrimitive.NUMBER)
            .addInsertValues("null", "9223372036854775807", "-9223372036854775808")
            .addExpectedValues(null, "9223372036854775807", "-9223372036854775808")
            .build());
    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("BIGINT")
            .airbyteType(JsonSchemaPrimitive.NUMBER)
            .addInsertValues("null", "9223372036854775807", "-9223372036854775808")
            .addExpectedValues(null, "9223372036854775807", "-9223372036854775808")
            .build());
    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("SMALLINT")
            .airbyteType(JsonSchemaPrimitive.NUMBER)
            .addInsertValues("null", "9223372036854775807", "-9223372036854775808")
            .addExpectedValues(null, "9223372036854775807", "-9223372036854775808")
            .build());
    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("TINYINT")
            .airbyteType(JsonSchemaPrimitive.NUMBER)
            .addInsertValues("null", "9223372036854775807", "-9223372036854775808")
            .addExpectedValues(null, "9223372036854775807", "-9223372036854775808")
            .build());
    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("BYTEINT")
            .airbyteType(JsonSchemaPrimitive.NUMBER)
            .addInsertValues("null", "9223372036854775807", "-9223372036854775808")
            .addExpectedValues(null, "9223372036854775807", "-9223372036854775808")
            .build());
    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("NUMBER")
            .airbyteType(JsonSchemaPrimitive.NUMBER)
            .fullSourceDataType("NUMBER(10,5)")
            .addInsertValues("10.12345")
            .addExpectedValues("10.12345")
            .build());
    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("DOUBLE")
            .airbyteType(JsonSchemaPrimitive.NUMBER)
            .addInsertValues("null", "-9007199254740991", "9007199254740991")
            .addExpectedValues(null, "-9.007199254740991E15", "9.007199254740991E15")
            .build());
    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("FLOAT")
            .airbyteType(JsonSchemaPrimitive.NUMBER)
            .addInsertValues("10e-308", "10e+307")
            .addExpectedValues("1.0E-307", "1.0E308")
            .build());
    // TODO should be fixed in scope of https://github.com/airbytehq/airbyte/issues/4316
    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("FLOAT")
            .airbyteType(JsonSchemaPrimitive.NUMBER)
            .addInsertValues("'NaN'", "'inf'", "'-inf'")
            .addExpectedValues(null, null, null)
            .build());

    // Data Types for Text Strings
    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("VARCHAR")
            .airbyteType(JsonSchemaPrimitive.STRING)
            .addInsertValues("null", "'тест'", "'⚡ test ��'",
                "'!\"#$%&\\'()*+,-./:;<=>?\\@[\\]^_\\`{|}~'")
            .addExpectedValues(null, "тест", "⚡ test ��", "!\"#$%&'()*+,-./:;<=>?@[]^_`|~")
            .build());
    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("STRING")
            .airbyteType(JsonSchemaPrimitive.STRING)
            .addInsertValues("null", "'テスト'")
            .addExpectedValues(null, "テスト")
            .build());
    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("TEXT")
            .airbyteType(JsonSchemaPrimitive.STRING)
            .addInsertValues("null", "'-\041-'", "'-\\x25-'")
            .addExpectedValues(null, "-!-", "-%-")
            .build());
    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("CHAR")
            .airbyteType(JsonSchemaPrimitive.STRING)
            .addInsertValues("null", "'a'", "'ス'", "'\041'", "'ї'")
            .addExpectedValues(null, "a", "ス", "!", "ї")
            .build());

    // Data Types for Binary Strings
    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("BINARY")
            .airbyteType(JsonSchemaPrimitive.STRING)
            .addInsertValues("null", "to_binary('HELP', 'UTF-8')")
            .addExpectedValues(null, "SEVMUA==")
            .build());

    // Logical Data Types
    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("BOOLEAN")
            .airbyteType(JsonSchemaPrimitive.BOOLEAN)
            .addInsertValues("null", "'true'", "5", "'false'", "0", "TO_BOOLEAN('y')",
                "TO_BOOLEAN('n')")
            .addExpectedValues(null, "true", "true", "false", "false", "true", "false")
            .build());

    // Date & Time Data Types
    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("DATE")
            .airbyteType(JsonSchemaPrimitive.STRING)
            .addInsertValues("null", "'0001-01-01'", "'9999-12-31'")
            .addExpectedValues(null, "0001-01-01T00:00:00Z", "9999-12-31T00:00:00Z")
            .build());
    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("DATETIME")
            .airbyteType(JsonSchemaPrimitive.STRING)
            .addInsertValues("null", "'0001-01-01 00:00:00'", "'9999-12-31 23:59:59'")
            .addExpectedValues(null, "0001-01-01T00:00:00Z", "9999-12-31T23:59:59Z")
            .build());
    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("TIME")
            .airbyteType(JsonSchemaPrimitive.STRING)
            .addInsertValues("null", "'00:00:00'", "'1:59 PM'", "'23:59:59'")
            .addExpectedValues(null, "1970-01-01T00:00:00Z", "1970-01-01T13:59:00Z",
                "1970-01-01T23:59:59Z")
            .build());
    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("TIMESTAMP")
            .airbyteType(JsonSchemaPrimitive.STRING)
            .addInsertValues("null", "'2018-03-22 12:00:00.123'")
            .addExpectedValues(null, "2018-03-22T12:00:00Z")
            .build());
    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("TIMESTAMP_LTZ")
            .airbyteType(JsonSchemaPrimitive.STRING)
            .addInsertValues("null", "'2018-03-22 12:00:00.123 +05:00'")
            .addExpectedValues(null, "2018-03-22T07:00:00Z")
            .build());
    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("TIMESTAMP_NTZ")
            .airbyteType(JsonSchemaPrimitive.STRING)
            .addInsertValues("null", "'2018-03-22 12:00:00.123 +05:00'")
            .addExpectedValues(null, "2018-03-22T12:00:00Z")
            .build());
    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("TIMESTAMP_TZ")
            .airbyteType(JsonSchemaPrimitive.STRING)
            .addInsertValues("null", "'2018-03-22 12:00:00.123 +05:00'")
            .addExpectedValues(null, "2018-03-22T07:00:00Z")
            .build());

    // Semi-structured Data Types
    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("VARIANT")
            .airbyteType(JsonSchemaPrimitive.STRING)
            .insertPatternSql(INSERT_SEMI_STRUCTURED_SQL)
            .addInsertValues("null",
                "parse_json(' { \"key1\": \"value1\", \"key2\": \"value2\" } ')")
            .addExpectedValues(null, "{\n  \"key1\": \"value1\",\n  \"key2\": \"value2\"\n}")
            .build());
    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("ARRAY")
            .airbyteType(JsonSchemaPrimitive.STRING)
            .insertPatternSql(INSERT_SEMI_STRUCTURED_SQL)
            .addInsertValues("null", "array_construct(1, 2, 3)")
            .addExpectedValues(null, "[\n  1,\n  2,\n  3\n]")
            .build());
    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("OBJECT")
            .airbyteType(JsonSchemaPrimitive.STRING)
            .insertPatternSql(INSERT_SEMI_STRUCTURED_SQL)
            .addInsertValues("null",
                "parse_json(' { \"outer_key1\": { \"inner_key1A\": \"1a\", \"inner_key1B\": \"1b\" }, \"outer_key2\": { \"inner_key2\": 2 } } ')")
            .addExpectedValues(null,
                "{\n  \"outer_key1\": {\n    \"inner_key1A\": \"1a\",\n    \"inner_key1B\": \"1b\"\n  },\n  \"outer_key2\": {\n    \"inner_key2\": 2\n  }\n}")
            .build());

    // Geospatial Data Types
    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("GEOGRAPHY")
            .airbyteType(JsonSchemaPrimitive.STRING)
            .addInsertValues("null", "'POINT(-122.35 37.55)'",
                "'LINESTRING(-124.20 42.00, -120.01 41.99)'")
            .addExpectedValues(null,
                "{\n  \"coordinates\": [\n    -122.35,\n    37.55\n  ],\n  \"type\": \"Point\"\n}",
                "{\n  \"coordinates\": [\n    [\n      -124.2,\n      42\n    ],\n    [\n      -120.01,\n      41.99\n    ]\n  ],\n  \"type\": \"LineString\"\n}")
            .build());
  }

}
