/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.io.airbyte.integration_tests.sources;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.Database;
import io.airbyte.db.factory.DSLContextFactory;
import io.airbyte.db.factory.DatabaseDriver;
import io.airbyte.integrations.standardtest.source.AbstractSourceDatabaseTypeTest;
import io.airbyte.integrations.standardtest.source.TestDataHolder;
import io.airbyte.integrations.standardtest.source.TestDestinationEnv;
import io.airbyte.protocol.models.JsonSchemaType;
import java.util.List;
import org.jooq.DSLContext;
import org.jooq.SQLDialect;
import org.testcontainers.containers.PostgreSQLContainer;
import org.testcontainers.utility.MountableFile;

public class CdcPostgresSourceDatatypeTest extends AbstractSourceDatabaseTypeTest {

  private static final String SCHEMA_NAME = "test";
  private static final String SLOT_NAME_BASE = "debezium_slot";
  private static final String PUBLICATION = "publication";
  private PostgreSQLContainer<?> container;
  private JsonNode config;

  @Override
  protected Database setupDatabase() throws Exception {

    container = new PostgreSQLContainer<>("postgres:13-alpine")
        .withCopyFileToContainer(MountableFile.forClasspathResource("postgresql.conf"),
            "/etc/postgresql/postgresql.conf")
        .withCommand("postgres -c config_file=/etc/postgresql/postgresql.conf");
    container.start();

    /**
     * The publication is not being set as part of the config and because of it
     * {@link io.airbyte.integrations.source.postgres.PostgresSource#isCdc(JsonNode)} returns false, as
     * a result no test in this class runs through the cdc path.
     */
    final JsonNode replicationMethod = Jsons.jsonNode(ImmutableMap.builder()
        .put("method", "CDC")
        .put("replication_slot", SLOT_NAME_BASE)
        .put("publication", PUBLICATION)
        .build());
    config = Jsons.jsonNode(ImmutableMap.builder()
        .put("host", container.getHost())
        .put("port", container.getFirstMappedPort())
        .put("database", container.getDatabaseName())
        .put("schemas", List.of(SCHEMA_NAME))
        .put("username", container.getUsername())
        .put("password", container.getPassword())
        .put("replication_method", replicationMethod)
        .put("ssl", false)
        .build());

    final DSLContext dslContext = DSLContextFactory.create(
        config.get("username").asText(),
        config.get("password").asText(),
        DatabaseDriver.POSTGRESQL.getDriverClassName(),
        String.format(DatabaseDriver.POSTGRESQL.getUrlFormatString(),
            config.get("host").asText(),
            config.get("port").asInt(),
            config.get("database").asText()), SQLDialect.POSTGRES);
    final Database database = new Database(dslContext);

    database.query(ctx -> {
      ctx.execute("SELECT pg_create_logical_replication_slot('" + SLOT_NAME_BASE + "', 'pgoutput');");
      ctx.execute("CREATE PUBLICATION " + PUBLICATION + " FOR ALL TABLES;");

      return null;
    });

    database.query(ctx -> ctx.fetch("CREATE SCHEMA TEST;"));
    database.query(ctx -> ctx.fetch("CREATE TYPE mood AS ENUM ('sad', 'ok', 'happy');"));
    database.query(ctx -> ctx.fetch("CREATE TYPE inventory_item AS (\n"
        + "    name            text,\n"
        + "    supplier_id     integer,\n"
        + "    price           numeric\n"
        + ");"));

    database.query(ctx -> ctx.fetch("SET TIMEZONE TO 'MST'"));
    return database;
  }

  @Override
  protected String getNameSpace() {
    return SCHEMA_NAME;
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
  protected void tearDown(final TestDestinationEnv testEnv) {
    container.close();
  }

  @Override
  protected void initTests() {
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
            .sourceType("bit")
            .fullSourceDataType("BIT(3)")
            .airbyteType(JsonSchemaType.NUMBER)
            .addInsertValues("B'101'", "B'111'", "null")
            .addExpectedValues("101", "111", null)
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

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("cidr")
            .airbyteType(JsonSchemaType.STRING)
            .addInsertValues("null", "'192.168.100.128/25'", "'192.168/24'", "'192.168.1'",
                "'128.1'", "'2001:4f8:3:ba::/64'")
            .addExpectedValues(null, "192.168.100.128/25", "192.168.0.0/24", "192.168.1.0/24",
                "128.1.0.0/16", "2001:4f8:3:ba::/64")
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("date")
            .airbyteType(JsonSchemaType.STRING)
            .addInsertValues("'January 7, 1999'", "'1999-01-08'", "'1/9/1999'", "'January 10, 99 BC'", "'January 11, 99 AD'", "null")
            .addExpectedValues("1999-01-07T00:00:00Z", "1999-01-08T00:00:00Z", "1999-01-09T00:00:00Z", "0099-01-10T00:00:00Z", "1999-01-11T00:00:00Z",
                null)
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("float8")
            .airbyteType(JsonSchemaType.NUMBER)
            .addInsertValues("'123'", "'1234567890.1234567'", "'-Infinity'", "'Infinity'", "'NaN'", "null")
            .addExpectedValues("123.0", "1.2345678901234567E9", "-Infinity", "Infinity", "NaN", null)
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("float")
            .airbyteType(JsonSchemaType.NUMBER)
            .addInsertValues("'123'", "'1234567890.1234567'", "'-Infinity'", "'Infinity'", "'NaN'", "null")
            .addExpectedValues("123.0", "1.2345678901234567E9", "-Infinity", "Infinity", "NaN", null)
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
            .addInsertValues("null", "'P1Y2M3DT4H5M6S'", "'PT4H5M6S'", "'-300'", "'-178000000'",
                "'178000000'", "'1-2'", "'3 4:05:06'", "'P0002-02-03T04:05:06'")
            .addExpectedValues(null, "1 year 2 mons 3 days 04:05:06", "04:05:06", "-00:05:00", "-49444:26:40",
                "49444:26:40", "1 year 2 mons 00:00:00", "3 days 04:05:06", "2 year 2 mons 3 days 04:05:06")
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
            .sourceType("macaddr")
            .airbyteType(JsonSchemaType.STRING)
            .addInsertValues("null", "'08:00:2b:01:02:03'", "'08-00-2b-01-02-04'",
                "'08002b:010205'")
            .addExpectedValues(null, "08:00:2b:01:02:03", "08:00:2b:01:02:04", "08:00:2b:01:02:05")
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("macaddr8")
            .airbyteType(JsonSchemaType.STRING)
            .addInsertValues("null", "'08:00:2b:01:02:03:04:05'", "'08-00-2b-01-02-03-04-06'",
                "'08002b:0102030407'")
            .addExpectedValues(null, "08:00:2b:01:02:03:04:05", "08:00:2b:01:02:03:04:06",
                "08:00:2b:01:02:03:04:07")
            .build());

    // Max values for Money type should be: "-92233720368547758.08", "92233720368547758.07",
    // debezium return rounded value for values more than 999999999999999 and less than
    // -999999999999999,
    // we map these value as null;
    // opened issue https://github.com/airbytehq/airbyte/issues/7338
    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("money")
            .airbyteType(JsonSchemaType.STRING)
            .addInsertValues("null", "'999.99'", "'1,000.01'", "'-999999999999.99'", "'-999999999999999'", "'999999999999.99'", "'999999999999999'",
                "'-92233720368547758.08'", "'92233720368547758.07'")
            .addExpectedValues(null, "999.99", "1000.01", "-999999999999.99", "-999999999999999", "999999999999.99", "999999999999999",
                null, null)
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("numeric")
            .airbyteType(JsonSchemaType.NUMBER)
            .addInsertValues("'99999'", "'NAN'", "10000000000000000000000000000000000000", null)
            .addExpectedValues("99999", "NAN", "10000000000000000000000000000000000000", null)
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("decimal")
            .airbyteType(JsonSchemaType.NUMBER)
            .addInsertValues("99999", "5.1", "0", "'NAN'", "null")
            .addExpectedValues("99999", "5.1", "0", "NAN", null)
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("numeric")
            .fullSourceDataType("numeric(13,4)")
            .airbyteType(JsonSchemaType.NUMBER)
            .addInsertValues("0.1880", "10.0000", "5213.3468", "'NAN'", "null")
            .addExpectedValues("0.1880", "10.0000", "5213.3468", "NAN", null)
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
            .addInsertValues("null", "'04:05:06'", "'2021-04-12 05:06:07'", "'04:05 PM'")
            .addExpectedValues(null, "04:05:06", "05:06:07", "16:05:00")
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("timetz")
            .airbyteType(JsonSchemaType.STRING)
            .addInsertValues("null", "'04:05:06+03'", "'2021-04-12 05:06:07+00'", "'060708-03'")
            .addExpectedValues(null, "04:05:06+03", "05:06:07+00", "06:07:08-03")
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("timestamp")
            .airbyteType(JsonSchemaType.STRING)
            .addInsertValues("TIMESTAMP '2004-10-19 10:23:54'", "TIMESTAMP '2004-10-19 10:23:54.123456'", "null")
            .addExpectedValues("2004-10-19T10:23:54.000000Z", "2004-10-19T10:23:54.123456Z", null)
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("timestamptz")
            .airbyteType(JsonSchemaType.STRING)
            .addInsertValues("TIMESTAMP WITH TIME ZONE '2004-10-19 10:23:54+03'", "TIMESTAMP WITH TIME ZONE '2004-10-19 10:23:54.123456+03'", "null")
            .addExpectedValues("2004-10-19T07:23:54Z", "2004-10-19T07:23:54.123456Z", null)
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("tsvector")
            .airbyteType(JsonSchemaType.STRING)
            .addInsertValues("to_tsvector('The quick brown fox jumped over the lazy dog.')")
            .addExpectedValues("'brown':3 'dog':9 'fox':4 'jumped':5 'lazy':8 'over':6 'quick':2 'the':1,7")
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("uuid")
            .airbyteType(JsonSchemaType.STRING)
            .addInsertValues("'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11'", "null")
            .addExpectedValues("a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11", null)
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("xml")
            .airbyteType(JsonSchemaType.STRING)
            .addInsertValues(
                "XMLPARSE (DOCUMENT '<?xml version=\"1.0\"?><book><title>Manual</title><chapter>...</chapter></book>')",
                "null", "''")
            .addExpectedValues("<book><title>Manual</title><chapter>...</chapter></book>", null, "")
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
            .sourceType("inventory_item")
            .airbyteType(JsonSchemaType.STRING)
            .addInsertValues("ROW('fuzzy dice', 42, 1.99)", "null")
            .addExpectedValues("(\"fuzzy dice\",42,1.99)", null)
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("tsrange")
            .airbyteType(JsonSchemaType.STRING)
            .addInsertValues("'(2010-01-01 14:30, 2010-01-01 15:30)'", "null")
            .addExpectedValues("(\"2010-01-01 14:30:00\",\"2010-01-01 15:30:00\")", null)
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("box")
            .airbyteType(JsonSchemaType.STRING)
            .addInsertValues("'((3,7),(15,18))'", "'((0,0),(0,0))'", "null")
            .addExpectedValues("(15.0,18.0),(3.0,7.0)", "(0.0,0.0),(0.0,0.0)", null)
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("circle")
            .airbyteType(JsonSchemaType.STRING)
            .addInsertValues("'(5,7),10'", "'(0,0),0'", "'(-10,-4),10'", "null")
            .addExpectedValues("<(5.0,7.0),10.0>", "<(0.0,0.0),0.0>", "<(-10.0,-4.0),10.0>", null)
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("line")
            .airbyteType(JsonSchemaType.STRING)
            .addInsertValues("'{4,5,6}'", "'{0,1,0}'", "null")
            .addExpectedValues("{4.0,5.0,6.0}", "{0.0,1.0,0.0}", null)
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("lseg")
            .airbyteType(JsonSchemaType.STRING)
            .addInsertValues("'((3,7),(15,18))'", "'((0,0),(0,0))'", "null")
            .addExpectedValues("[(3.0,7.0),(15.0,18.0)]", "[(0.0,0.0),(0.0,0.0)]", null)
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("path")
            .airbyteType(JsonSchemaType.STRING)
            .addInsertValues("'((3,7),(15.5,18.2))'", "'((0,0),(0,0))'", "null")
            .addExpectedValues("((3.0,7.0),(15.5,18.2))", "((0.0,0.0),(0.0,0.0))", null)
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("point")
            .airbyteType(JsonSchemaType.NUMBER)
            .addInsertValues("'(3,7)'", "'(0,0)'", "'(999999999999999999999999,0)'", "null")
            .addExpectedValues("(3.0,7.0)", "(0.0,0.0)", "(1.0E24,0.0)", null)
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("polygon")
            .airbyteType(JsonSchemaType.STRING)
            .addInsertValues("'((3,7),(15,18))'", "'((0,0),(0,0))'",
                "'((0,0),(999999999999999999999999,0))'", "null")
            .addExpectedValues("((3.0,7.0),(15.0,18.0))", "((0.0,0.0),(0.0,0.0))", "((0.0,0.0),(1.0E24,0.0))", null)
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("real")
            .airbyteType(JsonSchemaType.STRING)
            .addInsertValues("'123'", "'1234567890.1234567'", "null")
            .addExpectedValues("123.0", "1.23456794E9", null)
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("tsvector")
            .airbyteType(JsonSchemaType.STRING)
            .addInsertValues("to_tsvector('The quick brown fox jumped over the lazy dog.')")
            .addExpectedValues("'brown':3 'dog':9 'fox':4 'jumped':5 'lazy':8 'over':6 'quick':2 'the':1,7")
            .build());
  }

}
