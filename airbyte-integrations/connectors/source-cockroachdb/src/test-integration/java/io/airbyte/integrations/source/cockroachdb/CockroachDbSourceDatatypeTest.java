/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.cockroachdb;

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
import io.airbyte.protocol.models.JsonSchemaType;
import java.sql.SQLException;
import java.util.Objects;
import java.util.Set;
import org.jooq.DSLContext;
import org.jooq.SQLDialect;
import org.junit.jupiter.api.Disabled;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.testcontainers.containers.CockroachContainer;

@Disabled
public class CockroachDbSourceDatatypeTest extends AbstractSourceDatabaseTypeTest {

  private CockroachContainer container;
  private JsonNode config;
  private DSLContext dslContext;
  private static final Logger LOGGER = LoggerFactory
      .getLogger(CockroachDbSourceDatatypeTest.class);

  @Override
  protected Database setupDatabase() throws SQLException {
    container = new CockroachContainer("cockroachdb/cockroach:v20.2.18");
    container.start();

    config = Jsons.jsonNode(ImmutableMap.builder()
        .put(JdbcUtils.HOST_KEY, Objects.requireNonNull(container.getContainerInfo()
            .getNetworkSettings()
            .getNetworks()
            .entrySet().stream()
            .findFirst()
            .get().getValue().getIpAddress()))
        .put(JdbcUtils.PORT_KEY, container.getExposedPorts().get(1))
        .put(JdbcUtils.DATABASE_KEY, container.getDatabaseName())
        .put(JdbcUtils.USERNAME_KEY, container.getUsername())
        .put(JdbcUtils.PASSWORD_KEY, container.getPassword())
        .put(JdbcUtils.SSL_KEY, false)
        .build());
    LOGGER.warn("PPP:config:" + config);

    dslContext = DSLContextFactory.create(
        config.get(JdbcUtils.USERNAME_KEY).asText(),
        config.get(JdbcUtils.PASSWORD_KEY).asText(),
        DatabaseDriver.POSTGRESQL.getDriverClassName(),
        String.format(DatabaseDriver.POSTGRESQL.getUrlFormatString(),
            config.get(JdbcUtils.HOST_KEY).asText(),
            config.get(JdbcUtils.PORT_KEY).asInt(),
            config.get(JdbcUtils.DATABASE_KEY).asText()),
        SQLDialect.POSTGRES);
    final Database database = new Database(dslContext);

    database.query(ctx -> ctx.fetch("CREATE SCHEMA TEST;"));
    database.query(ctx -> ctx.fetch("CREATE TYPE mood AS ENUM ('sad', 'ok', 'happy');"));
    return database;
  }

  @Override
  protected String getNameSpace() {
    return "test";
  }

  @Override
  protected String getImageName() {
    return "airbyte/source-cockroachdb:dev";
  }

  @Override
  protected JsonNode getConfig() {
    return config;
  }

  @Override
  protected void tearDown(final TestDestinationEnv testEnv) {
    container.close();
  }

  @Override
  protected void initTests() {
    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("array")
            .fullSourceDataType("STRING[]")
            .airbyteType(JsonSchemaType.ARRAY)
            .addInsertValues("ARRAY['sky', 'road', 'car']", "null")
            .addExpectedValues("[\"sky\",\"road\",\"car\"]", null)
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("bit")
            .fullSourceDataType("BIT(3)")
            .airbyteType(JsonSchemaType.NUMBER)
            .addInsertValues("B'101'")
            .addExpectedValues("101")
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("bigint")
            .airbyteType(JsonSchemaType.NUMBER)
            .addInsertValues("-9223372036854775808", "9223372036854775807", "0", "null")
            .addExpectedValues("-9223372036854775808", "9223372036854775807", "0", null)
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("bigserial")
            .airbyteType(JsonSchemaType.NUMBER)
            .addInsertValues("1", "9223372036854775807", "0", "-9223372036854775808")
            .addExpectedValues("1", "9223372036854775807", "0", "-9223372036854775808")
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("serial")
            .airbyteType(JsonSchemaType.NUMBER)
            .addInsertValues("1", "2147483647", "0", "-2147483647")
            .addExpectedValues("1", "2147483647", "0", "-2147483647")
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("smallserial")
            .airbyteType(JsonSchemaType.NUMBER)
            .addInsertValues("1", "32767", "0", "-32767")
            .addExpectedValues("1", "32767", "0", "-32767")
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("bit_varying")
            .fullSourceDataType("BIT VARYING(5)")
            .airbyteType(JsonSchemaType.NUMBER)
            .addInsertValues("B'101'", "null")
            .addExpectedValues("101", null)
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("boolean")
            .airbyteType(JsonSchemaType.BOOLEAN)
            .addInsertValues("true", "'yes'", "'1'", "false", "'no'", "'0'", "null")
            .addExpectedValues("true", "true", "true", "false", "false", "false", null)
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("bytea")
            .fullSourceDataType("bytea[]")
            .airbyteType(JsonSchemaType.OBJECT)
            .addInsertValues("ARRAY['☃'::bytes, 'ї'::bytes]")
            .addExpectedValues("[\"\\\\xe29883\",\"\\\\xd197\"]")
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("blob")
            .airbyteType(JsonSchemaType.OBJECT)
            .addInsertValues("decode('1234', 'hex')")
            .addExpectedValues("EjQ=")
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("character")
            .airbyteType(JsonSchemaType.STRING)
            .addInsertValues("'a'", "'*'", "null")
            .addExpectedValues("a", "*", null)
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("character")
            .fullSourceDataType("character(8)")
            .airbyteType(JsonSchemaType.STRING)
            .addInsertValues("'{asb123}'", "'{asb12}'")
            .addExpectedValues("{asb123}", "{asb12} ")
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("varchar")
            .airbyteType(JsonSchemaType.STRING)
            .addInsertValues("'a'", "'abc'", "'Миші йдуть на південь, не питай чому;'", "'櫻花分店'",
                "''", "null", "'\\xF0\\x9F\\x9A\\x80'")
            .addExpectedValues("a", "abc", "Миші йдуть на південь, не питай чому;", "櫻花分店", "",
                null, "\\xF0\\x9F\\x9A\\x80")
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("varchar")
            .fullSourceDataType("character(12)")
            .airbyteType(JsonSchemaType.STRING)
            .addInsertValues("'a'", "'abc'", "'Миші йдуть;'", "'櫻花分店'",
                "''", "null")
            .addExpectedValues("a           ", "abc         ", "Миші йдуть; ", "櫻花分店        ",
                "            ", null)
            .build());
    for (final String type : Set.of("date", "date not null default '0000-00-00'")) {

    }
    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("date")
            .airbyteType(JsonSchemaType.STRING)
            .addInsertValues("'1999-01-08'", "null", "'16-12-06'")
            .addExpectedValues("1999-01-08", null, "2016-12-06")
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("float8")
            .airbyteType(JsonSchemaType.NUMBER)
            .addInsertValues("'123'", "'1234567890.1234567'", "null", "'infinity'",
                "'+infinity'", "'+inf'", "'inf'", "'-inf'", "'-infinity'", "'nan'")
            .addExpectedValues("123.0", "1.2345678901234567E9", null,
                "Infinity", "Infinity", "Infinity", "Infinity", "-Infinity", "-Infinity", "NaN")
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("float")
            .airbyteType(JsonSchemaType.NUMBER)
            .addInsertValues("'123'", "'1234567890.1234567'", "null", "'infinity'",
                "'+infinity'", "'+inf'", "'inf'", "'-inf'", "'-infinity'", "'nan'")
            .addExpectedValues("123.0", "1.2345678901234567E9", null, "Infinity",
                "Infinity", "Infinity", "Infinity", "-Infinity", "-Infinity", "NaN")
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("inet")
            .airbyteType(JsonSchemaType.STRING)
            .addInsertValues("'198.24.10.0/24'", "'198.24.10.0'", "'198.10/8'", "null")
            .addExpectedValues("198.24.10.0/24", "198.24.10.0", "198.10.0.0/8", null)
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("int")
            .airbyteType(JsonSchemaType.NUMBER)
            .addInsertValues("null", "-2147483648", "2147483647")
            .addExpectedValues(null, "-2147483648", "2147483647")
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("interval")
            .airbyteType(JsonSchemaType.STRING)
            .addInsertValues("null", "'P1Y2M3DT4H5M6S'", "'-178000000'", "'178000000'")
            .addExpectedValues(null, "1 year 2 mons 3 days 04:05:06", "-49444:26:40", "49444:26:40")
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("json")
            .airbyteType(JsonSchemaType.STRING)
            .addInsertValues("null", "'{\"a\": 10, \"b\": 15}'")
            .addExpectedValues(null, "{\"a\": 10, \"b\": 15}")
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("jsonb")
            .airbyteType(JsonSchemaType.STRING)
            .addInsertValues("null", "'[1, 2, 3]'::jsonb")
            .addExpectedValues(null, "[1, 2, 3]")
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("numeric")
            .airbyteType(JsonSchemaType.NUMBER)
            .addInsertValues("'99999'", "null")
            .addExpectedValues("99999", null)
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("decimal")
            .airbyteType(JsonSchemaType.NUMBER)
            .addInsertValues("'+inf'", "999", "'-inf'", "'+infinity'", "'-infinity'", "'nan'")
            .addExpectedValues("Infinity", "999", "-Infinity", "Infinity", "-Infinity", "NaN")
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("smallint")
            .airbyteType(JsonSchemaType.NUMBER)
            .addInsertValues("null", "-32768", "32767")
            .addExpectedValues(null, "-32768", "32767")
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("text")
            .airbyteType(JsonSchemaType.STRING)
            .addInsertValues("'a'", "'abc'", "'Миші йдуть;'", "'櫻花分店'",
                "''", "null", "'\\xF0\\x9F\\x9A\\x80'")
            .addExpectedValues("a", "abc", "Миші йдуть;", "櫻花分店", "", null, "\\xF0\\x9F\\x9A\\x80")
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("time")
            .airbyteType(JsonSchemaType.STRING)
            .addInsertValues("'04:05:06'", null)
            .addExpectedValues("04:05:06")
            .addNullExpectedValue()
            .build());

    // Time (04:05:06) would be represented like "1970-01-01T04:05:06Z"
    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("timetz")
            .airbyteType(JsonSchemaType.STRING)
            .addInsertValues("'04:05:06Z'", null)
            .addExpectedValues("04:05:06.000000Z")
            .addNullExpectedValue()
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("timestamp")
            .airbyteType(JsonSchemaType.STRING)
            .addInsertValues("TIMESTAMP '2004-10-19 10:23:54'", "TIMESTAMP '2004-10-19 10:23:54.123456'", "null")
            .addExpectedValues("2004-10-19T10:23:54", "2004-10-19T10:23:54.123456", null)
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("uuid")
            .airbyteType(JsonSchemaType.STRING)
            .addInsertValues("'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11'", "null")
            .addExpectedValues("a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11", null)
            .build());

    // preconditions for this test are set at the time of database creation (setupDatabase method)
    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("mood")
            .airbyteType(JsonSchemaType.STRING)
            .addInsertValues("'happy'", "null")
            .addExpectedValues("happy", null)
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("text")
            .fullSourceDataType("text[]")
            .airbyteType(JsonSchemaType.ARRAY)
            .addInsertValues("'{10000, 10000, 10000, 10000}'", "null")
            .addExpectedValues("[\"10000\",\"10000\",\"10000\",\"10000\"]", null)
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("int")
            .fullSourceDataType("int[]")
            .airbyteType(JsonSchemaType.ARRAY)
            .addInsertValues("'{10000, 10000, 10000, 10000}'", "null")
            .addExpectedValues("[\"10000\",\"10000\",\"10000\",\"10000\"]", null)
            .build());

  }

}
