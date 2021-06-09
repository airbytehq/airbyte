package io.airbyte.integrations.io.airbyte.integration_tests.sources;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.Database;
import io.airbyte.db.Databases;
import io.airbyte.integrations.standardtest.source.SourceComprehensiveTest;
import io.airbyte.integrations.standardtest.source.TestDataHolder;
import io.airbyte.integrations.standardtest.source.TestDestinationEnv;
import io.airbyte.protocol.models.JsonSchemaPrimitive;
import java.sql.SQLException;
import org.jooq.SQLDialect;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.testcontainers.containers.PostgreSQLContainer;

public class PostresSourceComprehensiveTest extends SourceComprehensiveTest {

  private PostgreSQLContainer<?> container;
  private JsonNode config;
  private static final Logger LOGGER = LoggerFactory
      .getLogger(PostresSourceComprehensiveTest.class);

  @Override
  protected Database setupDatabase() throws SQLException {
    container = new PostgreSQLContainer<>("postgres:13-alpine");
    container.start();

    config = Jsons.jsonNode(ImmutableMap.builder()
        .put("host", container.getHost())
        .put("port", container.getFirstMappedPort())
        .put("database", container.getDatabaseName())
        .put("username", container.getUsername())
        .put("password", container.getPassword())
        .put("ssl", false)
        .build());
    LOGGER.warn("PPP:config:" + config);

    final Database database = Databases.createDatabase(
        config.get("username").asText(),
        config.get("password").asText(),
        String.format("jdbc:postgresql://%s:%s/%s",
            config.get("host").asText(),
            config.get("port").asText(),
            config.get("database").asText()),
        "org.postgresql.Driver",
        SQLDialect.POSTGRES);

    database.query(ctx -> ctx.fetch("CREATE SCHEMA TEST;"));

    return database;
  }


  @Override
  protected String getImageName() {
    return "airbyte/source-postgres:dev";
  }

  @Override
  protected JsonNode getConfig() {
    return config;
  }

  @Override
  protected void tearDown(TestDestinationEnv testEnv) {
    container.close();
  }

  @Override
  protected void initTests() {
    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("bigint")
            .createTablePatternSql(
                "CREATE TABLE test.%1$s(id integer primary key, test_column %2$s);")
            .airbyteType(JsonSchemaPrimitive.NUMBER)
            .addInsertValues("-9223372036854775808", "9223372036854775807", "0", "null")
            .addExpectedValues("-9223372036854775808", "9223372036854775807", "0", null)
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("bigserial")
            .createTablePatternSql(
                "CREATE TABLE test.%1$s(id integer primary key, test_column %2$s);")
            .airbyteType(JsonSchemaPrimitive.NUMBER)
            .addInsertValues("1", "9223372036854775807", "0", "-9223372036854775808")
            .addExpectedValues("1", "9223372036854775807", "0", "-9223372036854775808")
            .build());

    //BUG https://github.com/airbytehq/airbyte/issues/3932
//    addDataTypeTestData(
//        TestDataHolder.builder()
//            .sourceType("bit")
//            .createTablePatternSql(
//                "CREATE TABLE test.%1$s(id integer primary key, test_column %2$s);")
//            .fullSourceDataType("BIT(3)")
//            .airbyteType(JsonSchemaPrimitive.NUMBER)
//            .addInsertValues("B'101'")
//            .addExpectedValues("101")
//            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("bit_varying")
            .createTablePatternSql(
                "CREATE TABLE test.%1$s(id integer primary key, test_column %2$s);")
            .fullSourceDataType("BIT VARYING(5)")
            .airbyteType(JsonSchemaPrimitive.NUMBER)
            .addInsertValues("B'101'", "null")
            .addExpectedValues("101", null)
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("boolean")
            .createTablePatternSql(
                "CREATE TABLE test.%1$s(id integer primary key, test_column %2$s);")
            .airbyteType(JsonSchemaPrimitive.BOOLEAN)
            .addInsertValues("true", "'yes'", "'1'", "false", "'no'", "'0'", "null")
            .addExpectedValues("true", "true", "true", "false", "false", "false", null)
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("bytea")
            .createTablePatternSql(
                "CREATE TABLE test.%1$s(id integer primary key, test_column %2$s);")
            .airbyteType(JsonSchemaPrimitive.OBJECT)
            .addInsertValues("decode('1234', 'hex')")
            .addExpectedValues("EjQ=")
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("character")
            .createTablePatternSql(
                "CREATE TABLE test.%1$s(id integer primary key, test_column %2$s);")
            .airbyteType(JsonSchemaPrimitive.STRING)
            .addInsertValues("'a'", "'*'", "null")
            .addExpectedValues("a", "*", null)
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("character")
            .fullSourceDataType("character(8)")
            .createTablePatternSql(
                "CREATE TABLE test.%1$s(id integer primary key, test_column %2$s);")
            .airbyteType(JsonSchemaPrimitive.STRING)
            .addInsertValues("'{asb123}'", "'{asb12}'")
            .addExpectedValues("{asb123}", "{asb12} ")
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("varchar")
            .createTablePatternSql(
                "CREATE TABLE test.%1$s(id integer primary key, test_column %2$s);")
            .airbyteType(JsonSchemaPrimitive.STRING)
            .addInsertValues("'a'", "'abc'", "'Миші йдуть на південь, не питай чому;'", "'櫻花分店'",
                "''", "null")
            .addExpectedValues("a", "abc", "Миші йдуть на південь, не питай чому;", "櫻花分店", "",
                null)
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("varchar")
            .fullSourceDataType("character(12)")
            .createTablePatternSql(
                "CREATE TABLE test.%1$s(id integer primary key, test_column %2$s);")
            .airbyteType(JsonSchemaPrimitive.STRING)
            .addInsertValues("'a'", "'abc'", "'Миші йдуть;'", "'櫻花分店'",
                "''", "null")
            .addExpectedValues("a           ", "abc         ", "Миші йдуть; ", "櫻花分店        ",
                "            ", null)
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("cidr")
            .createTablePatternSql(
                "CREATE TABLE test.%1$s(id integer primary key, test_column %2$s);")
            .airbyteType(JsonSchemaPrimitive.STRING)
            .addInsertValues("null", "'192.168.100.128/25'", "'192.168/24'", "'192.168.1'",
                "'128.1'", "'2001:4f8:3:ba::/64'")
            .addExpectedValues(null, "192.168.100.128/25", "192.168.0.0/24", "192.168.1.0/24",
                "128.1.0.0/16", "2001:4f8:3:ba::/64")
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("date")
            .airbyteType(JsonSchemaPrimitive.STRING)
            .addInsertValues("null")
            .addNullExpectedValue()
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("date")
            .createTablePatternSql(
                "CREATE TABLE test.%1$s(id integer primary key, test_column %2$s);")
            .airbyteType(JsonSchemaPrimitive.STRING)
            .addInsertValues("'1999-01-08'")
            .addExpectedValues("1999-01-08T00:00:00Z")
            .build());

  }
}
