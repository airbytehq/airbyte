package io.airbyte.integrations.io.airbyte.integration_tests.sources;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.Database;
import io.airbyte.db.Databases;
import io.airbyte.integrations.source.db2.Db2Source;
import io.airbyte.integrations.standardtest.source.SourceComprehensiveTest;
import io.airbyte.integrations.standardtest.source.TestDataHolder;
import io.airbyte.integrations.standardtest.source.TestDestinationEnv;
import io.airbyte.protocol.models.JsonSchemaPrimitive;
import org.jooq.SQLDialect;
import org.testcontainers.containers.Db2Container;

public class Db2SourceComprehensiveTest extends SourceComprehensiveTest {

  private Db2Container container;
  private JsonNode config;

  @Override
  protected String getImageName() {
    return "airbyte/source-db2:dev";
  }

  @Override
  protected JsonNode getConfig() throws Exception {
    return config;
  }

  @Override
  protected void tearDown(TestDestinationEnv testEnv) throws Exception {
    container.close();
  }

  @Override
  protected Database setupDatabase() throws Exception {
    container = new Db2Container("ibmcom/db2:11.5.5.0").acceptLicense();
    container.start();

    config = Jsons.jsonNode(ImmutableMap.builder()
        .put("host", container.getHost())
        .put("port", container.getFirstMappedPort())
        .put("db", container.getDatabaseName())
        .put("username", container.getUsername())
        .put("password", container.getPassword())
        .build());

    final Database database = Databases.createDatabase(
        config.get("username").asText(),
        config.get("password").asText(),
        String.format("jdbc:db2://%s:%s/%s",
            config.get("host").asText(),
            config.get("port").asText(),
            config.get("db").asText()),
        Db2Source.DRIVER_CLASS,
        SQLDialect.DEFAULT);

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
            .sourceType("SMALLINT")
            .airbyteType(JsonSchemaPrimitive.NUMBER)
            .addInsertValues("null", "-32768", "32767")
            .addExpectedValues(null, "-32768", "32767")
            .build());
    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("INTEGER")
            .airbyteType(JsonSchemaPrimitive.NUMBER)
            .addInsertValues("null", "-2147483648", "2147483647")
            .addExpectedValues(null, "-2147483648", "2147483647")
            .build());
    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("BIGINT")
            .airbyteType(JsonSchemaPrimitive.NUMBER)
            .addInsertValues("null", "-9223372036854775808", "9223372036854775807")
            .addExpectedValues(null, "-9223372036854775808", "9223372036854775807")
            .build());
    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("DECIMAL")
            .airbyteType(JsonSchemaPrimitive.NUMBER)
            .addInsertValues("null", "DECIMAL(1,1)") // TODO
            .addExpectedValues(null, "1")
            .build());
    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("REAL")
            .airbyteType(JsonSchemaPrimitive.NUMBER)
            .addInsertValues("null", "0", "CAST('-3.4028234663852886E38' AS REAL)", "REAL('-1.1754943508222875e-38')", "REAL(1.1754943508222875e-38)", "3.4028234663852886E38")
            .addExpectedValues(null, "0.0", "-3.4028235E38", "-1.17549435E-38", "1.17549435E-38", "3.4028235E38") // during insertion values are rounded, that's why such values are expected
            .build());
    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("DOUBLE")
            .airbyteType(JsonSchemaPrimitive.NUMBER)
            .addInsertValues("null", "DOUBLE('-1.7976931348623157E+308')", "DOUBLE('-2.2250738585072014E-308')", "DOUBLE('2.2250738585072014E-308')", "DOUBLE('1.7976931348623157E+308')")
            .addExpectedValues(null, "-1.7976931348623157E308", "-2.2250738585072014E-308", "2.2250738585072014E-308", "1.7976931348623157E308")
            .build());
    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("DECFLOAT")
            .airbyteType(JsonSchemaPrimitive.NUMBER)
            .addInsertValues("null", "0") // TODO
            .addExpectedValues(null, "0")
            .build());

    // Boolean values
    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("BOOLEAN")
            .airbyteType(JsonSchemaPrimitive.BOOLEAN)
            .addInsertValues("null", "'t'", "'true'", "'y'", "'yes'", "'on'", "'1'", "'f'", "'false'", "'n'", "'no'", "'off'", "'0'")
            .addExpectedValues(null, "true", "true", "true", "true", "true", "true", "false", "false", "false", "false", "false", "false")
            .build());

    // Character, graphic, binary strings
    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("CHAR")
            .airbyteType(JsonSchemaPrimitive.STRING)
            .addInsertValues("null", "'a'", "' '", "'*'") // CHAR length range 1 - 255, no empty value allowed
            .addExpectedValues(null, "a", " ", "*")
            .build());
    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("VARCHAR")
            .airbyteType(JsonSchemaPrimitive.STRING)
            .fullSourceDataType("VARCHAR(128)") // TODO
            .addInsertValues("null", "'тест'", "'⚡ test ��'")
            .addExpectedValues(null, "тест", "⚡ test ��")
            .build());
    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("VARCHAR")
            .airbyteType(JsonSchemaPrimitive.STRING)
            .fullSourceDataType("VARCHAR(128)")
            .addInsertValues("null", "chr(33) || chr(34) || chr(35) || chr(36) || chr(37) || chr(38) || chr(39) || chr(40) || chr(41)")
            .addExpectedValues(null, "!\"#$%&'()")
            .build());
    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("NCHAR")
            .airbyteType(JsonSchemaPrimitive.STRING)
            .addInsertValues("null", "' '") // TODO
            .addExpectedValues(null, " ")
            .build());
    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("NVARCHAR")
            .airbyteType(JsonSchemaPrimitive.STRING)
            .fullSourceDataType("NVARCHAR(128)")
            .addInsertValues("null", "' '")// TODO
            .addExpectedValues(null, " ")
            .build());
    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("GRAPHIC")
            .airbyteType(JsonSchemaPrimitive.STRING)
            .addInsertValues("null", "' '") // TODO
            .addExpectedValues(null, " ")
            .build());
    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("VARGRAPHIC")
            .airbyteType(JsonSchemaPrimitive.STRING)
            .fullSourceDataType("VARGRAPHIC(8)")
            .addInsertValues("null", "VARGRAPHIC(100500, ',')")
            .addExpectedValues(null, "100500")
            .build());
    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("VARBINARY")
            .airbyteType(JsonSchemaPrimitive.STRING)
            .fullSourceDataType("VARBINARY(32)")
            .addInsertValues("null", "VARBINARY('test VARBINARY type', 19)")
            .addExpectedValues(null, "dGVzdCBWQVJCSU5BUlkgdHlwZQ==")
            .build());

    // Large objects
    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("BLOB")
            .airbyteType(JsonSchemaPrimitive.STRING)
            .addInsertValues("null", "BLOB(' ')", "BLOB('test BLOB type')")
            .addExpectedValues(null, "IA==", "dGVzdCBCTE9CIHR5cGU=")
            .build());
    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("CLOB")
            .airbyteType(JsonSchemaPrimitive.STRING)
            .addInsertValues("null", "' '", "CLOB('test CLOB type')")
            .addExpectedValues(null, " ", "test CLOB type")
            .build());
    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("NCLOB")
            .airbyteType(JsonSchemaPrimitive.STRING)
            .addInsertValues("null", "' '", "NCLOB('test NCLOB type')")
            .addExpectedValues(null, " ", "test NCLOB type")
            .build());

    // XML values
    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("XML")
            .airbyteType(JsonSchemaPrimitive.STRING)
            .addInsertValues("null", "XMLPARSE (DOCUMENT '<?xml version=\"1.0\"?><book><title>Manual</title><chapter>...</chapter></book>' PRESERVE WHITESPACE)")
            .addExpectedValues(null, "<book><title>Manual</title><chapter>...</chapter></book>")
            .build());

    // Datetime values
    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("DATE")
            .airbyteType(JsonSchemaPrimitive.STRING)
            .addInsertValues("null", "'0001-01-01'", "'9999-12-31'")
            .addExpectedValues(null, "0001-01-01T00:00:00Z", "9999-12-31T00:00:00Z")
            .build());
    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("TIME")
            .airbyteType(JsonSchemaPrimitive.STRING)
            .addInsertValues("null", "'00.00.00'", "'1:59 PM'", "'23.59.59'")
            .addExpectedValues(null, "1970-01-01T00:00:00Z", "1970-01-01T13:59:00Z", "1970-01-01T23:59:59Z")
            .build());
    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("TIMESTAMP")
            .airbyteType(JsonSchemaPrimitive.STRING)
            .addInsertValues("null", "'2018-03-22-12.00.00.123'", "'20180322125959'", "'20180101 12:00:59 PM'")
            .addExpectedValues(null, "2018-03-22T12:00:00Z", "2018-03-22T12:59:59Z", "2018-01-01T12:00:59Z") // milliseconds values are erased
            .build());
  }
}
