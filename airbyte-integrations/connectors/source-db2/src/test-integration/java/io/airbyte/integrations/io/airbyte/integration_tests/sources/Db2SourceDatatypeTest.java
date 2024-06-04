/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.io.airbyte.integration_tests.sources;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.cdk.db.Database;
import io.airbyte.cdk.db.factory.DSLContextFactory;
import io.airbyte.cdk.db.factory.DatabaseDriver;
import io.airbyte.cdk.db.jdbc.JdbcUtils;
import io.airbyte.cdk.integrations.standardtest.source.AbstractSourceDatabaseTypeTest;
import io.airbyte.cdk.integrations.standardtest.source.TestDataHolder;
import io.airbyte.cdk.integrations.standardtest.source.TestDestinationEnv;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.source.db2.Db2Source;
import io.airbyte.protocol.models.JsonSchemaType;
import org.jooq.DSLContext;
import org.jooq.SQLDialect;
import org.junit.jupiter.api.Disabled;
import org.testcontainers.containers.Db2Container;

@Disabled
public class Db2SourceDatatypeTest extends AbstractSourceDatabaseTypeTest {

  private static final String CREATE_TABLE_SQL = "CREATE TABLE %1$s(%2$s INTEGER NOT NULL PRIMARY KEY, %3$s %4$s)";
  private static final String CREATE_TABLE_SQL_UNICODE = CREATE_TABLE_SQL + " CCSID UNICODE";

  private Db2Container container;
  private JsonNode config;
  private DSLContext dslContext;

  @Override
  protected String getImageName() {
    return "airbyte/source-db2:dev";
  }

  @Override
  protected JsonNode getConfig() throws Exception {
    return config;
  }

  @Override
  protected void tearDown(final TestDestinationEnv testEnv) {
    container.close();
  }

  @Override
  protected Database setupDatabase() throws Exception {
    container = new Db2Container("ibmcom/db2:11.5.5.0").acceptLicense();
    container.start();

    config = Jsons.jsonNode(ImmutableMap.builder()
        .put(JdbcUtils.HOST_KEY, container.getHost())
        .put(JdbcUtils.PORT_KEY, container.getFirstMappedPort())
        .put("db", container.getDatabaseName())
        .put(JdbcUtils.USERNAME_KEY, container.getUsername())
        .put(JdbcUtils.PASSWORD_KEY, container.getPassword())
        .put(JdbcUtils.ENCRYPTION_KEY, Jsons.jsonNode(ImmutableMap.builder()
            .put("encryption_method", "unencrypted")
            .build()))
        .build());

    dslContext = DSLContextFactory.create(
        config.get(JdbcUtils.USERNAME_KEY).asText(),
        config.get(JdbcUtils.PASSWORD_KEY).asText(),
        Db2Source.DRIVER_CLASS,
        String.format(DatabaseDriver.DB2.getUrlFormatString(),
            config.get(JdbcUtils.HOST_KEY).asText(),
            config.get(JdbcUtils.PORT_KEY).asInt(),
            config.get("db").asText()),
        SQLDialect.DEFAULT);
    final Database database = new Database(dslContext);

    database.query(ctx -> ctx.fetch("CREATE SCHEMA TEST"));

    return database;
  }

  @Override
  protected String getNameSpace() {
    return "TEST";
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
    // Numbers
    addDataTypeTestData(
        TestDataHolder.builder()
            .createTablePatternSql(CREATE_TABLE_SQL)
            .sourceType("SMALLINT")
            .airbyteType(JsonSchemaType.NUMBER)
            .addInsertValues("null", "-32768", "32767")
            .addExpectedValues(null, "-32768", "32767")
            .build());
    addDataTypeTestData(
        TestDataHolder.builder()
            .createTablePatternSql(CREATE_TABLE_SQL)
            .sourceType("INTEGER")
            .airbyteType(JsonSchemaType.NUMBER)
            .addInsertValues("null", "-2147483648", "2147483647")
            .addExpectedValues(null, "-2147483648", "2147483647")
            .build());
    addDataTypeTestData(
        TestDataHolder.builder()
            .createTablePatternSql(CREATE_TABLE_SQL)
            .sourceType("BIGINT")
            .airbyteType(JsonSchemaType.NUMBER)
            .addInsertValues("null", "-9223372036854775808", "9223372036854775807")
            .addExpectedValues(null, "-9223372036854775808", "9223372036854775807")
            .build());
    addDataTypeTestData(
        TestDataHolder.builder()
            .createTablePatternSql(CREATE_TABLE_SQL)
            .sourceType("DECIMAL")
            .airbyteType(JsonSchemaType.NUMBER)
            .fullSourceDataType("DECIMAL(31, 0)")
            .addInsertValues("null", "1", "DECIMAL((-1 + 10E+29), 31, 0)", "DECIMAL((1 - 10E+29), 31, 0)")
            .addExpectedValues(null, "1", "%.0f".formatted(Double.valueOf("1.0E30")), "%.0f".formatted(Double.valueOf("-1.0E30")))
            .build());
    addDataTypeTestData(
        TestDataHolder.builder()
            .createTablePatternSql(CREATE_TABLE_SQL)
            .sourceType("REAL")
            .airbyteType(JsonSchemaType.NUMBER)
            .addInsertValues("null", "0", "CAST('-3.4028234663852886E38' AS REAL)", "REAL('-1.1754943508222875e-38')", "REAL(1.1754943508222875e-38)",
                "3.4028234663852886E38")
            .addExpectedValues(null, "0.0", "-3.4028235E38", "-1.17549435E-38", "1.17549435E-38", "3.4028235E38") // during insertion values are
                                                                                                                  // rounded, that's why such values
                                                                                                                  // are expected
            .build());
    addDataTypeTestData(
        TestDataHolder.builder()
            .createTablePatternSql(CREATE_TABLE_SQL)
            .sourceType("DOUBLE")
            .airbyteType(JsonSchemaType.NUMBER)
            .addInsertValues("null", "DOUBLE('-1.7976931348623157E+308')", "DOUBLE('-2.2250738585072014E-308')", "DOUBLE('2.2250738585072014E-308')",
                "DOUBLE('1.7976931348623157E+308')")
            .addExpectedValues(null, "-1.7976931348623157E308", "-2.2250738585072014E-308", "2.2250738585072014E-308", "1.7976931348623157E308")
            .build());

    // DECFLOAT type tests
    addDataTypeTestData(
        TestDataHolder.builder()
            .createTablePatternSql(CREATE_TABLE_SQL)
            .sourceType("DECFLOAT")
            .airbyteType(JsonSchemaType.NUMBER)
            .fullSourceDataType("DECFLOAT(16)")
            .addInsertValues("null", "0", "1.0E308", "1.0E-306")
            .addExpectedValues(null, "0", "1E+308", "1E-306")
            .build());
    addDataTypeTestData(
        TestDataHolder.builder()
            .createTablePatternSql(CREATE_TABLE_SQL)
            .sourceType("DECFLOAT")
            .airbyteType(JsonSchemaType.NUMBER)
            .fullSourceDataType("DECFLOAT(34)")
            .addInsertValues("null", "0", "DECFLOAT(10E+307, 34)", "DECFLOAT(10E-307, 34)")
            .addExpectedValues(null, "0", "1E+308", "1E-306")
            .build());
    addDataTypeTestData(
        TestDataHolder.builder()
            .createTablePatternSql(CREATE_TABLE_SQL)
            .sourceType("DECFLOAT")
            .airbyteType(JsonSchemaType.NUMBER)
            .addInsertValues("SNaN", "NaN", "Infinity", "-Infinity")
            .addExpectedValues("NaN", "NaN", "Infinity", "-Infinity")
            .build());

    // Boolean values
    addDataTypeTestData(
        TestDataHolder.builder()
            .createTablePatternSql(CREATE_TABLE_SQL)
            .sourceType("BOOLEAN")
            .airbyteType(JsonSchemaType.BOOLEAN)
            .addInsertValues("null", "'t'", "'true'", "'y'", "'yes'", "'on'", "'1'", "'f'", "'false'", "'n'", "'no'", "'off'", "'0'")
            .addExpectedValues(null, "true", "true", "true", "true", "true", "true", "false", "false", "false", "false", "false", "false")
            .build());

    // Character, graphic, binary strings
    addDataTypeTestData(
        TestDataHolder.builder()
            .createTablePatternSql(CREATE_TABLE_SQL)
            .sourceType("CHAR")
            .airbyteType(JsonSchemaType.STRING)
            .addInsertValues("null", "'a'", "' '", "'*'")
            .addExpectedValues(null, "a", " ", "*")
            .build());
    addDataTypeTestData(
        TestDataHolder.builder()
            .createTablePatternSql(CREATE_TABLE_SQL)
            .sourceType("VARCHAR")
            .airbyteType(JsonSchemaType.STRING)
            .fullSourceDataType("VARCHAR(256)")
            .addInsertValues("null", "'тест'", "'⚡ test ��'", "'!\"#$%&\\''()*+,-./:;<=>?\\@[\\]^_\\`{|}~'")
            .addExpectedValues(null, "тест", "⚡ test ��", "!\"#$%&\\'()*+,-./:;<=>?\\@[\\]^_\\`{|}~")
            .build());
    addDataTypeTestData(
        TestDataHolder.builder()
            .createTablePatternSql(CREATE_TABLE_SQL)
            .sourceType("VARCHAR")
            .airbyteType(JsonSchemaType.STRING)
            .fullSourceDataType("VARCHAR(128)")
            .addInsertValues("null", "chr(33) || chr(34) || chr(35) || chr(36) || chr(37) || chr(38) || chr(39) || chr(40) || chr(41)")
            .addExpectedValues(null, "!\"#$%&'()")
            .build());
    addDataTypeTestData(
        TestDataHolder.builder()
            .createTablePatternSql(CREATE_TABLE_SQL_UNICODE)
            .sourceType("NCHAR")
            .airbyteType(JsonSchemaType.STRING)
            .addInsertValues("null", "' '", "'テ'")
            .addExpectedValues(null, " ", "テ")
            .build());
    addDataTypeTestData(
        TestDataHolder.builder()
            .createTablePatternSql(CREATE_TABLE_SQL_UNICODE)
            .sourceType("NVARCHAR")
            .airbyteType(JsonSchemaType.STRING)
            .fullSourceDataType("NVARCHAR(128)")
            .addInsertValues("null", "' '", "'テスト'")
            .addExpectedValues(null, " ", "テスト")
            .build());
    addDataTypeTestData(
        TestDataHolder.builder()
            .createTablePatternSql(CREATE_TABLE_SQL)
            .sourceType("GRAPHIC")
            .airbyteType(JsonSchemaType.STRING)
            .fullSourceDataType("GRAPHIC(8)")
            .addInsertValues("null", "' '", "'12345678'")
            .addExpectedValues(null, "        ", "12345678")
            .build());
    addDataTypeTestData(
        TestDataHolder.builder()
            .createTablePatternSql(CREATE_TABLE_SQL)
            .sourceType("VARGRAPHIC")
            .airbyteType(JsonSchemaType.STRING)
            .fullSourceDataType("VARGRAPHIC(8)")
            .addInsertValues("null", "VARGRAPHIC(100500, ',')")
            .addExpectedValues(null, "100500")
            .build());
    addDataTypeTestData(
        TestDataHolder.builder()
            .createTablePatternSql(CREATE_TABLE_SQL)
            .sourceType("VARBINARY")
            .airbyteType(JsonSchemaType.STRING)
            .fullSourceDataType("VARBINARY(32)")
            .addInsertValues("null", "VARBINARY('test VARBINARY type', 19)")
            .addExpectedValues(null, "dGVzdCBWQVJCSU5BUlkgdHlwZQ==")
            .build());

    // Large objects
    addDataTypeTestData(
        TestDataHolder.builder()
            .createTablePatternSql(CREATE_TABLE_SQL)
            .sourceType("BLOB")
            .airbyteType(JsonSchemaType.STRING)
            .addInsertValues("null", "BLOB(' ')", "BLOB('test BLOB type')")
            .addExpectedValues(null, "IA==", "dGVzdCBCTE9CIHR5cGU=")
            .build());
    addDataTypeTestData(
        TestDataHolder.builder()
            .createTablePatternSql(CREATE_TABLE_SQL)
            .sourceType("CLOB")
            .airbyteType(JsonSchemaType.STRING)
            .addInsertValues("null", "' '", "CLOB('test CLOB type')")
            .addExpectedValues(null, " ", "test CLOB type")
            .build());
    addDataTypeTestData(
        TestDataHolder.builder()
            .createTablePatternSql(CREATE_TABLE_SQL)
            .sourceType("NCLOB")
            .airbyteType(JsonSchemaType.STRING)
            .addInsertValues("null", "' '", "NCLOB('test NCLOB type')")
            .addExpectedValues(null, " ", "test NCLOB type")
            .build());

    // XML values
    addDataTypeTestData(
        TestDataHolder.builder()
            .createTablePatternSql(CREATE_TABLE_SQL)
            .sourceType("XML")
            .airbyteType(JsonSchemaType.STRING)
            .addInsertValues("null",
                "XMLPARSE (DOCUMENT '<?xml version=\"1.0\"?><book><title>Manual</title><chapter>...</chapter></book>' PRESERVE WHITESPACE)")
            .addExpectedValues(null, "<book><title>Manual</title><chapter>...</chapter></book>")
            .build());

    // Datetime values
    addDataTypeTestData(
        TestDataHolder.builder()
            .createTablePatternSql(CREATE_TABLE_SQL)
            .sourceType("DATE")
            .airbyteType(JsonSchemaType.STRING)
            .addInsertValues("null", "'0001-01-01'", "'9999-12-31'")
            .addExpectedValues(null, "0001-01-01", "9999-12-31")
            .build());
    addDataTypeTestData(
        TestDataHolder.builder()
            .createTablePatternSql(CREATE_TABLE_SQL)
            .sourceType("TIME")
            .airbyteType(JsonSchemaType.STRING)
            .addInsertValues("null", "'00.00.00'", "'1:59 PM'", "'23.59.59'")
            .addExpectedValues(null, "00:00:00.000000", "13:59:00.000000", "23:59:59")
            .build());
    addDataTypeTestData(
        TestDataHolder.builder()
            .createTablePatternSql(CREATE_TABLE_SQL)
            .sourceType("TIMESTAMP")
            .airbyteType(JsonSchemaType.STRING)
            .addInsertValues("null", "'2018-03-22-12.00.00.123'", "'2018-03-22-12.00.00.123456'", "'20180322125959'", "'20180101 12:00:59 PM'")
            .addExpectedValues(null, "2018-03-22T12:00:00.123", "2018-03-22T12:00:00.123456", "2018-03-22T12:59:59",
                "2018-01-01T12:00:59")
            .build());
  }

}
