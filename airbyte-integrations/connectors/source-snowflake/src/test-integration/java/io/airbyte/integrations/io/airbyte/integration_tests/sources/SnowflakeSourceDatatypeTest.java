/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.io.airbyte.integration_tests.sources;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.Database;
import io.airbyte.db.factory.DSLContextFactory;
import io.airbyte.db.factory.DatabaseDriver;
import io.airbyte.db.jdbc.JdbcUtils;
import io.airbyte.integrations.source.snowflake.SnowflakeSource;
import io.airbyte.integrations.standardtest.source.AbstractSourceDatabaseTypeTest;
import io.airbyte.integrations.standardtest.source.TestDataHolder;
import io.airbyte.integrations.standardtest.source.TestDestinationEnv;
import io.airbyte.protocol.models.JsonSchemaType;
import java.nio.file.Path;
import java.util.Map;
import org.apache.commons.lang3.RandomStringUtils;
import org.jooq.DSLContext;
import org.jooq.SQLDialect;

public class SnowflakeSourceDatatypeTest extends AbstractSourceDatabaseTypeTest {

  private static final String SCHEMA_NAME = "SOURCE_DATA_TYPE_TEST_"
      + RandomStringUtils.randomAlphanumeric(4).toUpperCase();
  private static final String INSERT_SEMI_STRUCTURED_SQL = "INSERT INTO %1$s (ID, TEST_COLUMN) SELECT %2$s, %3$s";

  private JsonNode config;
  private Database database;
  private DSLContext dslContext;

  @Override
  protected String getImageName() {
    return "airbyte/source-snowflake:dev";
  }

  @Override
  protected JsonNode getConfig() {
    return config;
  }

  @Override
  protected Database setupDatabase() throws Exception {
    config = Jsons.deserialize(IOs.readFile(Path.of("secrets/config.json")));

    dslContext = DSLContextFactory.create(
        config.get("credentials").get(JdbcUtils.USERNAME_KEY).asText(),
        config.get("credentials").get(JdbcUtils.PASSWORD_KEY).asText(),
        SnowflakeSource.DRIVER_CLASS,
        String.format(DatabaseDriver.SNOWFLAKE.getUrlFormatString(), config.get(JdbcUtils.HOST_KEY).asText()),
        SQLDialect.DEFAULT,
        Map.of(
            "role", config.get("role").asText(),
            "warehouse", config.get("warehouse").asText(),
            JdbcUtils.DATABASE_KEY, config.get(JdbcUtils.DATABASE_KEY).asText()));

    database = getDatabase();

    final String createSchemaQuery = String.format("CREATE SCHEMA IF NOT EXISTS %s", SCHEMA_NAME);
    database.query(ctx -> ctx.fetch(createSchemaQuery));
    return database;
  }

  private Database getDatabase() {
    return new Database(dslContext);
  }

  @Override
  protected void setupEnvironment(final TestDestinationEnv environment) throws Exception {
    super.setupEnvironment(environment);
  }

  @Override
  protected void tearDown(final TestDestinationEnv testEnv) throws Exception {
    try {
      final String dropSchemaQuery = String
          .format("DROP SCHEMA IF EXISTS %s", SCHEMA_NAME);
      database.query(ctx -> ctx.fetch(dropSchemaQuery));
    } finally {
      dslContext.close();
    }
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
    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("NUMBER")
            .airbyteType(JsonSchemaType.NUMBER)
            .addInsertValues("null", "99999999999999999999999999999999999999", "-99999999999999999999999999999999999999", "9223372036854775807",
                "-9223372036854775808")
            .addExpectedValues(null, "99999999999999999999999999999999999999", "-99999999999999999999999999999999999999", "9223372036854775807",
                "-9223372036854775808")
            .build());
    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("DECIMAL")
            .airbyteType(JsonSchemaType.NUMBER)
            .addInsertValues("null", "9223372036854775807", "-9223372036854775808")
            .addExpectedValues(null, "9223372036854775807", "-9223372036854775808")
            .build());
    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("NUMERIC")
            .airbyteType(JsonSchemaType.NUMBER)
            .addInsertValues("null", "99999999999999999999999999999999999999", "-99999999999999999999999999999999999999", "9223372036854775807",
                "-9223372036854775808")
            .addExpectedValues(null, "99999999999999999999999999999999999999", "-99999999999999999999999999999999999999", "9223372036854775807",
                "-9223372036854775808")
            .build());
    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("BIGINT")
            .airbyteType(JsonSchemaType.NUMBER)
            .addInsertValues("null", "99999999999999999999999999999999999999", "-99999999999999999999999999999999999999")
            .addExpectedValues(null, "99999999999999999999999999999999999999", "-99999999999999999999999999999999999999")
            .build());
    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("INT")
            .airbyteType(JsonSchemaType.NUMBER)
            .addInsertValues("null", "9223372036854775807", "-9223372036854775808")
            .addExpectedValues(null, "9223372036854775807", "-9223372036854775808")
            .build());
    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("BIGINT")
            .airbyteType(JsonSchemaType.NUMBER)
            .addInsertValues("null", "9223372036854775807", "-9223372036854775808")
            .addExpectedValues(null, "9223372036854775807", "-9223372036854775808")
            .build());
    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("SMALLINT")
            .airbyteType(JsonSchemaType.NUMBER)
            .addInsertValues("null", "9223372036854775807", "-9223372036854775808")
            .addExpectedValues(null, "9223372036854775807", "-9223372036854775808")
            .build());
    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("TINYINT")
            .airbyteType(JsonSchemaType.NUMBER)
            .addInsertValues("null", "9223372036854775807", "-9223372036854775808")
            .addExpectedValues(null, "9223372036854775807", "-9223372036854775808")
            .build());
    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("BYTEINT")
            .airbyteType(JsonSchemaType.NUMBER)
            .addInsertValues("null", "9223372036854775807", "-9223372036854775808")
            .addExpectedValues(null, "9223372036854775807", "-9223372036854775808")
            .build());
    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("NUMBER")
            .airbyteType(JsonSchemaType.NUMBER)
            .fullSourceDataType("NUMBER(10,5)")
            .addInsertValues("10.12345")
            .addExpectedValues("10.12345")
            .build());
    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("DOUBLE")
            .airbyteType(JsonSchemaType.NUMBER)
            .addInsertValues("null", "-9007199254740991", "9007199254740991")
            .addExpectedValues(null, "-9.00719925474099E15", "9.00719925474099E15")
            .build());
    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("FLOAT")
            .airbyteType(JsonSchemaType.NUMBER)
            .addInsertValues("10e-308", "10e+307")
            .addExpectedValues("1.0E-307", "1.0E308")
            .build());
    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("FLOAT")
            .airbyteType(JsonSchemaType.NUMBER)
            .addInsertValues("'NaN'", "'inf'", "'-inf'")
            .addExpectedValues("NaN", "Infinity", "-Infinity")
            .build());
    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("NUMBER")
            .airbyteType(JsonSchemaType.INTEGER)
            .fullSourceDataType("NUMBER(38,0)")
            .addInsertValues("9", "990", "9990", "999000", "999000000", "999000000000")
            .addExpectedValues("9", "990", "9990", "999000", "999000000", "999000000000")
            .build());

    // Data Types for Text Strings
    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("VARCHAR")
            .airbyteType(JsonSchemaType.STRING)
            .addInsertValues("null", "'тест'", "'⚡ test ��'",
                "'!\"#$%&\\'()*+,-./:;<=>?\\@[\\]^_\\`{|}~'")
            .addExpectedValues(null, "тест", "⚡ test ��", "!\"#$%&'()*+,-./:;<=>?@[]^_`|~")
            .build());
    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("STRING")
            .airbyteType(JsonSchemaType.STRING)
            .addInsertValues("null", "'テスト'")
            .addExpectedValues(null, "テスト")
            .build());
    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("TEXT")
            .airbyteType(JsonSchemaType.STRING)
            .addInsertValues("null", "'-\041-'", "'-\\x25-'")
            .addExpectedValues(null, "-!-", "-%-")
            .build());
    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("CHAR")
            .airbyteType(JsonSchemaType.STRING)
            .addInsertValues("null", "'a'", "'ス'", "'\041'", "'ї'")
            .addExpectedValues(null, "a", "ス", "!", "ї")
            .build());

    // Data Types for Binary Strings
    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("BINARY")
            .airbyteType(JsonSchemaType.STRING)
            .addInsertValues("null", "to_binary('HELP', 'UTF-8')")
            .addExpectedValues(null, "SEVMUA==")
            .build());

    // Logical Data Types
    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("BOOLEAN")
            .airbyteType(JsonSchemaType.BOOLEAN)
            .addInsertValues("null", "'true'", "5", "'false'", "0", "TO_BOOLEAN('y')",
                "TO_BOOLEAN('n')")
            .addExpectedValues(null, "true", "true", "false", "false", "true", "false")
            .build());

    // Date & Time Data Types
    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("DATE")
            .airbyteType(JsonSchemaType.STRING_DATE)
            .addInsertValues("null", "'0001-01-01'", "'9999-12-31'")
            .addExpectedValues(null, "0001-01-01", "9999-12-31")
            .build());
    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("DATETIME")
            .airbyteType(JsonSchemaType.STRING_TIMESTAMP_WITHOUT_TIMEZONE)
            .addInsertValues("null", "'0001-01-01 00:00:00'", "'9999-12-31 23:59:59'", "'9999-12-31 23:59:59.123456'")
            .addExpectedValues(null, "0001-01-01T00:00:00.000000", "9999-12-31T23:59:59.000000", "9999-12-31T23:59:59.123456")
            .build());
    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("TIME")
            .airbyteType(JsonSchemaType.STRING_TIME_WITHOUT_TIMEZONE)
            .addInsertValues("null", "'00:00:00'", "'1:59 PM'", "'23:59:59.123456'")
            .addExpectedValues(null, "00:00:00.000000", "13:59:00.000000",
                "23:59:59.123456")
            .build());
    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("TIMESTAMP")
            .airbyteType(JsonSchemaType.STRING_TIMESTAMP_WITHOUT_TIMEZONE)
            .addInsertValues("null", "'2018-03-22 12:00:00.123'", "'2018-03-22 12:00:00.123456'")
            .addExpectedValues(null, "2018-03-22T12:00:00.123000", "2018-03-22T12:00:00.123456")
            .build());
    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("TIMESTAMP_LTZ")
            .airbyteType(JsonSchemaType.STRING_TIMESTAMP_WITH_TIMEZONE)
            .addInsertValues("null", "'2018-03-22 12:00:00.123 +05:00'", "'2018-03-22 12:00:00.123456 +05:00'")
            .addExpectedValues(null, "2018-03-22T07:00:00.123000Z", "2018-03-22T07:00:00.123456Z")
            .build());
    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("TIMESTAMP_NTZ")
            .airbyteType(JsonSchemaType.STRING_TIMESTAMP_WITHOUT_TIMEZONE)
            .addInsertValues("null", "'2018-03-22 12:00:00.123 +05:00'", "'2018-03-22 12:00:00.123456 +05:00'")
            .addExpectedValues(null, "2018-03-22T12:00:00.123000", "2018-03-22T12:00:00.123456")
            .build());
    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("TIMESTAMP_TZ")
            .airbyteType(JsonSchemaType.STRING_TIMESTAMP_WITH_TIMEZONE)
            .addInsertValues("null", "'2018-03-22 12:00:00.123 +05:00'", "'2018-03-22 12:00:00.123456 +05:00'")
            .addExpectedValues(null, "2018-03-22T07:00:00.123000Z", "2018-03-22T07:00:00.123456Z")
            .build());

    // Semi-structured Data Types
    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("VARIANT")
            .airbyteType(JsonSchemaType.STRING)
            .insertPatternSql(INSERT_SEMI_STRUCTURED_SQL)
            .addInsertValues("null",
                "parse_json(' { \"key1\": \"value1\", \"key2\": \"value2\" } ')")
            .addExpectedValues(null, "{\n  \"key1\": \"value1\",\n  \"key2\": \"value2\"\n}")
            .build());
    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("ARRAY")
            .airbyteType(JsonSchemaType.STRING)
            .insertPatternSql(INSERT_SEMI_STRUCTURED_SQL)
            .addInsertValues("null", "array_construct(1, 2, 3)")
            .addExpectedValues(null, "[\n  1,\n  2,\n  3\n]")
            .build());
    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("OBJECT")
            .airbyteType(JsonSchemaType.STRING)
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
            .airbyteType(JsonSchemaType.STRING)
            .addInsertValues("null", "'POINT(-122.35 37.55)'",
                "'LINESTRING(-124.20 42.00, -120.01 41.99)'")
            .addExpectedValues(null,
                "{\n  \"coordinates\": [\n    -122.35,\n    37.55\n  ],\n  \"type\": \"Point\"\n}",
                "{\n  \"coordinates\": [\n    [\n      -124.2,\n      42\n    ],\n    [\n      -120.01,\n      41.99\n    ]\n  ],\n  \"type\": \"LineString\"\n}")
            .build());
  }

}
