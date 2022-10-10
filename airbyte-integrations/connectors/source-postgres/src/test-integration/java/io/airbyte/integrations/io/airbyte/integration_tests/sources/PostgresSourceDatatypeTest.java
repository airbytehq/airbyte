/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.io.airbyte.integration_tests.sources;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.Database;
import io.airbyte.db.factory.DSLContextFactory;
import io.airbyte.db.factory.DatabaseDriver;
import io.airbyte.db.jdbc.JdbcUtils;
import io.airbyte.integrations.standardtest.source.TestDataHolder;
import io.airbyte.integrations.standardtest.source.TestDestinationEnv;
import io.airbyte.integrations.util.HostPortResolver;
import java.sql.SQLException;

import io.airbyte.protocol.models.JsonSchemaPrimitive;
import io.airbyte.protocol.models.JsonSchemaType;
import org.jooq.SQLDialect;
import org.testcontainers.containers.PostgreSQLContainer;
import org.testcontainers.utility.MountableFile;

import static io.airbyte.protocol.models.JsonSchemaType.*;
import static io.airbyte.protocol.models.JsonSchemaType.STRING_TIMESTAMP_WITHOUT_TIMEZONE;

public class PostgresSourceDatatypeTest extends AbstractPostgresSourceDatatypeTest {

  @Override
  protected Database setupDatabase() throws SQLException {
    container = new PostgreSQLContainer<>("postgres:14-alpine")
        .withCopyFileToContainer(MountableFile.forClasspathResource("postgresql.conf"),
            "/etc/postgresql/postgresql.conf")
        .withCommand("postgres -c config_file=/etc/postgresql/postgresql.conf");
    container.start();
    final JsonNode replicationMethod = Jsons.jsonNode(ImmutableMap.builder()
        .put("method", "Standard")
        .build());
    config = Jsons.jsonNode(ImmutableMap.builder()
        .put(JdbcUtils.HOST_KEY, HostPortResolver.resolveHost(container))
        .put(JdbcUtils.PORT_KEY, HostPortResolver.resolvePort(container))
        .put(JdbcUtils.DATABASE_KEY, container.getDatabaseName())
        .put(JdbcUtils.USERNAME_KEY, container.getUsername())
        .put(JdbcUtils.PASSWORD_KEY, container.getPassword())
        .put(JdbcUtils.SSL_KEY, false)
        .put("replication_method", replicationMethod)
        .build());

    dslContext = DSLContextFactory.create(
        config.get(JdbcUtils.USERNAME_KEY).asText(),
        config.get(JdbcUtils.PASSWORD_KEY).asText(),
        DatabaseDriver.POSTGRESQL.getDriverClassName(),
        String.format(DatabaseDriver.POSTGRESQL.getUrlFormatString(),
            container.getHost(),
            container.getFirstMappedPort(),
            config.get(JdbcUtils.DATABASE_KEY).asText()),
        SQLDialect.POSTGRES);
    final Database database = new Database(dslContext);

    database.query(ctx -> {
      ctx.execute(String.format("CREATE SCHEMA %S;", SCHEMA_NAME));
      ctx.execute("CREATE TYPE mood AS ENUM ('sad', 'ok', 'happy');");
      ctx.execute("CREATE TYPE inventory_item AS (name text, supplier_id integer, price numeric);");
      // In one of the test case, we have some money values with currency symbol. Postgres can only
      // understand those money values if the symbol corresponds to the monetary locale setting. For
      // example,
      // if the locale is 'en_GB', '£100' is valid, but '$100' is not. So setting the monetary locate is
      // necessary here to make sure the unit test can pass, no matter what the locale the runner VM has.
      ctx.execute("SET lc_monetary TO 'en_US.utf8';");
      // Set up a fixed timezone here so that timetz and timestamptz always have the same time zone
      // wherever the tests are running on.
      ctx.execute("SET TIMEZONE TO 'MST'");
      ctx.execute("CREATE EXTENSION hstore;");
      return null;
    });

    return database;
  }

  @Override
  protected void tearDown(final TestDestinationEnv testEnv) {
    dslContext.close();
    container.close();
  }

  @Override
  public boolean testCatalog() {
    return true;
  }

  @Override
  protected void initTests() {
    super.initTests();
    addArraysTestData();
  }

  private void addArraysTestData() {
    addDataTypeTestData(
            TestDataHolder.builder()
                    .sourceType("int2_array")
                    .fullSourceDataType("INT2[]")
                    .airbyteType(JsonSchemaType.builder(JsonSchemaPrimitive.ARRAY)
                            .withItems(INTEGER)
                            .withAirbyteType("int2_array")
                            .build())
                    .addInsertValues("'{1,2,3}'","'{4,5,6}'")
                    .addExpectedValues("[1,2,3]","[4,5,6]")
                    .build());

    addDataTypeTestData(
            TestDataHolder.builder()
                    .sourceType("int4_array")
                    .fullSourceDataType("INT4[]")
                    .airbyteType(JsonSchemaType.builder(JsonSchemaPrimitive.ARRAY)
                            .withItems(INTEGER)
                            .withAirbyteType("int4_array")
                            .build())
                    .addInsertValues("'{-2147483648,2147483646}'")
                    .addExpectedValues("[-2147483648,2147483646]")
                    .build());

    addDataTypeTestData(
            TestDataHolder.builder()
                    .sourceType("int8_array")
                    .fullSourceDataType("INT8[]")
                    .airbyteType(JsonSchemaType.builder(JsonSchemaPrimitive.ARRAY)
                            .withItems(INTEGER)
                            .withAirbyteType("int8_array")
                            .build())
                    .addInsertValues("'{-9223372036854775808,9223372036854775801}'")
                    .addExpectedValues("[-9223372036854775808,9223372036854775801]")
                    .build());

    addDataTypeTestData(
            TestDataHolder.builder()
                    .sourceType("oid_array")
                    .fullSourceDataType("OID[]")
                    .airbyteType(JsonSchemaType.builder(JsonSchemaPrimitive.ARRAY)
                            .withItems(INTEGER)
                            .withAirbyteType("oid_array")
                            .build())
                    .addInsertValues("'{564182,234181}'")
                    .addExpectedValues("[564182,234181]")
                    .build());

    addDataTypeTestData(
            TestDataHolder.builder()
                    .sourceType("varchar_array")
                    .fullSourceDataType("VARCHAR[]")
                    .airbyteType(JsonSchemaType.builder(JsonSchemaPrimitive.ARRAY)
                            .withItems(JsonSchemaType.builder(JsonSchemaPrimitive.STRING)
                                    .build())
                            .withAirbyteType("varchar_array")
                            .build())
                    .addInsertValues("'{lorem ipsum,dolor sit,amet}'")
                    .addExpectedValues("[\"lorem ipsum\",\"dolor sit\",\"amet\"]")
                    .build());

    addDataTypeTestData(
            TestDataHolder.builder()
                    .sourceType("char_array")
                    .fullSourceDataType("CHAR(1)[]")
                    .airbyteType(JsonSchemaType.builder(JsonSchemaPrimitive.ARRAY)
                            .withItems(JsonSchemaType.builder(JsonSchemaPrimitive.STRING)
                                    .build())
                            .withAirbyteType("bpchar_array")
                            .build())
                    .addInsertValues("'{l,d,a}'")
                    .addExpectedValues("[\"l\",\"d\",\"a\"]")
                    .build());

    addDataTypeTestData(
            TestDataHolder.builder()
                    .sourceType("char_array")
                    .fullSourceDataType("BPCHAR(2)[]")
                    .airbyteType(JsonSchemaType.builder(JsonSchemaPrimitive.ARRAY)
                            .withItems(JsonSchemaType.builder(JsonSchemaPrimitive.STRING)
                                    .build())
                            .withAirbyteType("bpchar_array")
                            .build())
                    .addInsertValues("'{l,d,a}'")
                    .addExpectedValues("[\"l \",\"d \",\"a \"]")
                    .build());

    addDataTypeTestData(
            TestDataHolder.builder()
                    .sourceType("text_array")
                    .fullSourceDataType("TEXT[]")
                    .airbyteType(JsonSchemaType.builder(JsonSchemaPrimitive.ARRAY)
                            .withItems(JsonSchemaType.builder(JsonSchemaPrimitive.STRING)
                                    .build())
                            .withAirbyteType("text_array")
                            .build())
                    .addInsertValues("'{someeeeee loooooooooong teeeeext,vvvvvvveeeeeeeeeeeruyyyyyyyyy looooooooooooooooong teeeeeeeeeeeeeeext}'")
                    .addExpectedValues("[\"someeeeee loooooooooong teeeeext\",\"vvvvvvveeeeeeeeeeeruyyyyyyyyy looooooooooooooooong teeeeeeeeeeeeeeext\"]")
                    .build());

    addDataTypeTestData(
            TestDataHolder.builder()
                    .sourceType("name_array")
                    .fullSourceDataType("NAME[]")
                    .airbyteType(JsonSchemaType.builder(JsonSchemaPrimitive.ARRAY)
                            .withItems(JsonSchemaType.builder(JsonSchemaPrimitive.STRING)
                                    .build())
                            .withAirbyteType("name_array")
                            .build())
                    .addInsertValues("'{object,integer}'")
                    .addExpectedValues("[\"object\",\"integer\"]")
                    .build());

    addDataTypeTestData(
            TestDataHolder.builder()
                    .sourceType("numeric_array")
                    .fullSourceDataType("NUMERIC[]")
                    .airbyteType(JsonSchemaType.builder(JsonSchemaPrimitive.ARRAY)
                            .withItems(JsonSchemaType.builder(JsonSchemaPrimitive.NUMBER)
                                    .build())
                            .withAirbyteType("numeric_array")
                            .build())
                    .addInsertValues("'{131070.23,231072.476596593}'")
                    .addExpectedValues("[131070.23,231072.476596593]")
                    .build());

    addDataTypeTestData(
            TestDataHolder.builder()
                    .sourceType("decimal_array")
                    .fullSourceDataType("DECIMAL[]")
                    .airbyteType(JsonSchemaType.builder(JsonSchemaPrimitive.ARRAY)
                            .withItems(JsonSchemaType.builder(JsonSchemaPrimitive.NUMBER)
                                    .build())
                            .withAirbyteType("numeric_array")
                            .build())
                    .addInsertValues("'{131070.23,231072.476596593}'")
                    .addExpectedValues("[131070.23,231072.476596593]")
                    .build());

    addDataTypeTestData(
            TestDataHolder.builder()
                    .sourceType("float4_array")
                    .fullSourceDataType("FLOAT4[]")
                    .airbyteType(JsonSchemaType.builder(JsonSchemaPrimitive.ARRAY)
                            .withItems(JsonSchemaType.builder(JsonSchemaPrimitive.NUMBER)
                                    .build())
                            .withAirbyteType("float4_array")
                            .build())
                    .addInsertValues("'{131070.237689,231072.476596593}'")
                    .addExpectedValues("[131070.234,231072.48]")
                    .build());

    addDataTypeTestData(
            TestDataHolder.builder()
                    .sourceType("float8_array")
                    .fullSourceDataType("FLOAT8[]")
                    .airbyteType(JsonSchemaType.builder(JsonSchemaPrimitive.ARRAY)
                            .withItems(JsonSchemaType.builder(JsonSchemaPrimitive.NUMBER)
                                    .build())
                            .withAirbyteType("float8_array")
                            .build())
                    .addInsertValues("'{131070.237689,231072.476596593}'")
                    .addExpectedValues("[131070.237689,231072.476596593]")
                    .build());

    addDataTypeTestData(
            TestDataHolder.builder()
                    .sourceType("money_array")
                    .fullSourceDataType("MONEY[]")
                    .airbyteType(JsonSchemaType.builder(JsonSchemaPrimitive.ARRAY)
                            .withItems(JsonSchemaType.builder(JsonSchemaPrimitive.NUMBER)
                                    .build())
                            .withAirbyteType("money_array")
                            .build())
                    .addInsertValues("'{$999.99,$1001.01,$1.001}'")
                    .addExpectedValues("[999.99,1001.01,1.0]")
                    .build());

    addDataTypeTestData(
            TestDataHolder.builder()
                    .sourceType("bool_array")
                    .fullSourceDataType("BOOL[]")
                    .airbyteType(JsonSchemaType.builder(JsonSchemaPrimitive.ARRAY)
                            .withItems(JsonSchemaType.builder(JsonSchemaPrimitive.BOOLEAN)
                                    .build())
                            .withAirbyteType("bool_array")
                            .build())
                    .addInsertValues("'{true,yes,1,false,no,0,null}'")
                    .addExpectedValues("[true,true,true,false,false,false,null]")
                    .build());

    addDataTypeTestData(
            TestDataHolder.builder()
                    .sourceType("bit_array")
                    .fullSourceDataType("BIT[]")
                    .airbyteType(JsonSchemaType.builder(JsonSchemaPrimitive.ARRAY)
                            .withItems(JsonSchemaType.builder(JsonSchemaPrimitive.BOOLEAN)
                                    .build())
                            .withAirbyteType("bit_array")
                            .build())
                    .addInsertValues("'{null,1,0}'")
                    .addExpectedValues("[null,true,false]")
                    .build());

    addDataTypeTestData(
            TestDataHolder.builder()
                    .sourceType("bytea_array")
                    .fullSourceDataType("BYTEA[]")
                    .airbyteType(JsonSchemaType.builder(JsonSchemaPrimitive.ARRAY)
                            .withItems(JsonSchemaType.builder(JsonSchemaPrimitive.STRING)
                                    .build())
                            .withAirbyteType("bytea_array")
                            .build())
                    .addInsertValues("'{\\xA6697E974E6A320F454390BE03F74955E8978F1A6971EA6730542E37B66179BC,\\x4B52414B00000000000000000000000000000000000000000000000000000000}'")
                    .addExpectedValues("[\"eEE2Njk3RTk3NEU2QTMyMEY0NTQzOTBCRTAzRjc0OTU1RTg5NzhGMUE2OTcxRUE2NzMwNTQyRTM3QjY2MTc5QkM=\",\"eDRCNTI0MTRCMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDA=\"]")
                    .build());

    addDataTypeTestData(
            TestDataHolder.builder()
                    .sourceType("date_array")
                    .fullSourceDataType("DATE[]")
                    .airbyteType(JsonSchemaType.builder(JsonSchemaPrimitive.ARRAY)
                            .withItems(STRING_DATE)
                            .withAirbyteType("date_array")
                            .build())
                    .addInsertValues("'{1999-01-08,1991-02-10 BC}'")
                    .addExpectedValues("[\"1999-01-08\",\"1991-02-10 BC\"]")
                    .build());

    addDataTypeTestData(
            TestDataHolder.builder()
                    .sourceType("time_array")
                    .fullSourceDataType("TIME[]")
                    .airbyteType(JsonSchemaType.builder(JsonSchemaPrimitive.ARRAY)
                            .withItems(STRING_TIME_WITHOUT_TIMEZONE)
                            .withAirbyteType("time_without_timezone_array")
                            .build())
                    .addInsertValues("'{13:00:01,13:00:02+8,13:00:03-8,13:00:04Z,13:00:05.01234Z+8,13:00:00Z-8}'")
                    .addExpectedValues("[\"13:00:01.000000\",\"13:00:02.000000\",\"13:00:03.000000\",\"13:00:04.000000\",\"13:00:05.012340\",\"13:00:00.000000\"]")
                    .build());

    addDataTypeTestData(
            TestDataHolder.builder()
                    .sourceType("timetz_array")
                    .fullSourceDataType("TIMETZ[]")
                    .airbyteType(JsonSchemaType.builder(JsonSchemaPrimitive.ARRAY)
                            .withItems(STRING_TIME_WITH_TIMEZONE)
                            .withAirbyteType("time_with_timezone_array")
                            .build())
                    .addInsertValues("'{null,13:00:01,13:00:00+8,13:00:03-8,13:00:04Z,13:00:05.012345Z+8,13:00:06.00000Z-8}'")
                    .addExpectedValues("[null,\"13:00:01.000000-07:00\",\"13:00:00.000000+08:00\",\"13:00:03.000000-08:00\",\"13:00:04.000000Z\",\"13:00:05.012345-08:00\",\"13:00:06.000000+08:00\"]")
                    .build());

    addDataTypeTestData(
            TestDataHolder.builder()
                    .sourceType("timestamptz_array")
                    .fullSourceDataType("TIMESTAMPTZ[]")
                    .airbyteType(JsonSchemaType.builder(JsonSchemaPrimitive.ARRAY)
                            .withItems(STRING_TIMESTAMP_WITH_TIMEZONE)
                            .withAirbyteType("timestamp_with_timezone_array")
                            .build())
                    .addInsertValues("'{null,2004-10-19 10:23:00-08,2004-10-19 10:23:54.123456-08}'")
                    .addExpectedValues("[null,\"2004-10-19T18:23:00.000000Z\",\"2004-10-19T18:23:54.123456Z\"]")
                    .build());

    addDataTypeTestData(
            TestDataHolder.builder()
                    .sourceType("timestamp_array")
                    .fullSourceDataType("TIMESTAMP[]")
                    .airbyteType(JsonSchemaType.builder(JsonSchemaPrimitive.ARRAY)
                            .withItems(STRING_TIMESTAMP_WITHOUT_TIMEZONE)
                            .withAirbyteType("timestamp_without_timezone_array")
                            .build())
                    .addInsertValues("'{null,2004-10-19 10:23:00,2004-10-19 10:23:54.123456,3004-10-19 10:23:54.123456 BC}'")
                    .addExpectedValues("[null,\"2004-10-19T10:23:00.000000\",\"2004-10-19T10:23:54.123456\",\"3004-10-19T10:23:54.123456 BC\"]")
                    .build());
  }
}
