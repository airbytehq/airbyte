/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.io.airbyte.integration_tests.sources;

import static io.airbyte.protocol.models.JsonSchemaType.STRING_DATE;
import static io.airbyte.protocol.models.JsonSchemaType.STRING_TIMESTAMP_WITHOUT_TIMEZONE;
import static io.airbyte.protocol.models.JsonSchemaType.STRING_TIMESTAMP_WITH_TIMEZONE;
import static io.airbyte.protocol.models.JsonSchemaType.STRING_TIME_WITHOUT_TIMEZONE;
import static io.airbyte.protocol.models.JsonSchemaType.STRING_TIME_WITH_TIMEZONE;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.integrations.standardtest.source.AbstractSourceDatabaseTypeTest;
import io.airbyte.integrations.standardtest.source.TestDataHolder;
import io.airbyte.protocol.models.JsonSchemaPrimitiveUtil.JsonSchemaPrimitive;
import io.airbyte.protocol.models.JsonSchemaType;
import java.util.Set;
import org.jooq.DSLContext;
import org.testcontainers.containers.PostgreSQLContainer;

public abstract class AbstractPostgresSourceDatatypeTest extends AbstractSourceDatabaseTypeTest {

  protected PostgreSQLContainer<?> container;
  protected JsonNode config;
  protected DSLContext dslContext;
  protected static final String SCHEMA_NAME = "test";

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
  public boolean testCatalog() {
    return true;
  }

  // Test cases are sorted alphabetically based on the source type
  // See https://www.postgresql.org/docs/14/datatype.html
  @Override
  protected void initTests() {
    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("bigint")
            .airbyteType(JsonSchemaType.INTEGER)
            .addInsertValues("-9223372036854775808", "9223372036854775807", "0", "null")
            .addExpectedValues("-9223372036854775808", "9223372036854775807", "0", null)
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("bigserial")
            .airbyteType(JsonSchemaType.INTEGER)
            .addInsertValues("1", "9223372036854775807", "0", "-9223372036854775808")
            .addExpectedValues("1", "9223372036854775807", "0", "-9223372036854775808")
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("bit")
            .fullSourceDataType("BIT(1)")
            .airbyteType(JsonSchemaType.STRING)
            .addInsertValues("B'0'")
            .addExpectedValues("0")
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("bit")
            .fullSourceDataType("BIT(3)")
            .airbyteType(JsonSchemaType.STRING)
            .addInsertValues("B'101'")
            .addExpectedValues("101")
            .build());

    for (final String type : Set.of("bit varying", "varbit")) {
      addDataTypeTestData(
          TestDataHolder.builder()
              .sourceType("bit_varying")
              .fullSourceDataType("BIT VARYING(5)")
              .airbyteType(JsonSchemaType.STRING)
              .addInsertValues("B'101'", "null")
              .addExpectedValues("101", null)
              .build());
    }

    for (final String type : Set.of("boolean", "bool")) {
      addDataTypeTestData(
          TestDataHolder.builder()
              .sourceType(type)
              .airbyteType(JsonSchemaType.BOOLEAN)
              .addInsertValues("true", "'yes'", "'1'", "false", "'no'", "'0'", "null")
              .addExpectedValues("true", "true", "true", "false", "false", "false", null)
              .build());
    }

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("box")
            .airbyteType(JsonSchemaType.STRING)
            .addInsertValues("'((3,7),(15,18))'", "'((0,0),(0,0))'", "null")
            .addExpectedValues("(15.0,18.0),(3.0,7.0)", "(0.0,0.0),(0.0,0.0)", null)
            .build());

    // bytea stores variable length binary string
    // https://www.postgresql.org/docs/14/datatype-binary.html
    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("bytea")
            .airbyteType(JsonSchemaType.STRING)
            .addInsertValues("null", "decode('1234', 'hex')", "'1234'", "'abcd'", "'\\xabcd'")
            .addExpectedValues(null, "\\x1234", "\\x31323334", "\\x61626364", "\\xabcd")
            .build());

    for (final String type : Set.of("character", "char")) {
      addDataTypeTestData(
          TestDataHolder.builder()
              .sourceType(type)
              .airbyteType(JsonSchemaType.STRING)
              .addInsertValues("'a'", "'*'", "null")
              .addExpectedValues("a", "*", null)
              .build());

      addDataTypeTestData(
          TestDataHolder.builder()
              .sourceType(type)
              .fullSourceDataType(type + "(8)")
              .airbyteType(JsonSchemaType.STRING)
              .addInsertValues("'{asb123}'", "'{asb12}'")
              .addExpectedValues("{asb123}", "{asb12} ")
              .build());
    }

    for (final String type : Set.of("varchar", "text")) {
      addDataTypeTestData(
          TestDataHolder.builder()
              .sourceType(type)
              .airbyteType(JsonSchemaType.STRING)
              .addInsertValues("'a'", "'abc'", "'Миші йдуть на південь, не питай чому;'", "'櫻花分店'",
                  "''", "null", "'\\xF0\\x9F\\x9A\\x80'")
              .addExpectedValues("a", "abc", "Миші йдуть на південь, не питай чому;", "櫻花分店", "",
                  null, "\\xF0\\x9F\\x9A\\x80")
              .build());
    }

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("varchar")
            .fullSourceDataType("character varying(10)")
            .airbyteType(JsonSchemaType.STRING)
            .addInsertValues("'{asb123}'", "'{asb12}'")
            .addExpectedValues("{asb123}", "{asb12}")
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
            .sourceType("circle")
            .airbyteType(JsonSchemaType.STRING)
            .addInsertValues("'(5,7),10'", "'(0,0),0'", "'(-10,-4),10'", "null")
            .addExpectedValues("<(5.0,7.0),10.0>", "<(0.0,0.0),0.0>", "<(-10.0,-4.0),10.0>", null)
            .build());

    // Debezium does not handle era indicators (AD nd BC)
    // https://github.com/airbytehq/airbyte/issues/14590
    for (final String type : Set.of("date", "date not null default now()")) {
      addDataTypeTestData(
          TestDataHolder.builder()
              .sourceType("date")
              .fullSourceDataType(type)
              .airbyteType(JsonSchemaType.STRING_DATE)
              .addInsertValues("'1999-01-08'", "'1991-02-10 BC'")
              .addExpectedValues("1999-01-08", "1991-02-10 BC")
              .build());
    }

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("date")
            .airbyteType(JsonSchemaType.STRING_DATE)
            .addInsertValues("null")
            .addExpectedValues((String) null)
            .build());

    for (final String type : Set.of("double precision", "float", "float8")) {
      addDataTypeTestData(
          TestDataHolder.builder()
              .sourceType(type)
              .airbyteType(JsonSchemaType.NUMBER)
              .addInsertValues("'123'", "'1234567890.1234567'", "null")
              // Postgres source does not support these special values yet
              // https://github.com/airbytehq/airbyte/issues/8902
              // "'-Infinity'", "'Infinity'", "'NaN'", "null")
              .addExpectedValues("123.0", "1.2345678901234567E9", null)
              // "-Infinity", "Infinity", "NaN", null)
              .build());
    }

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("inet")
            .airbyteType(JsonSchemaType.STRING)
            .addInsertValues("'198.24.10.0/24'", "'198.24.10.0'", "'198.10/8'", "null")
            .addExpectedValues("198.24.10.0/24", "198.24.10.0", "198.10.0.0/8", null)
            .build());

    for (final String type : Set.of("integer", "int", "int4")) {
      addDataTypeTestData(
          TestDataHolder.builder()
              .sourceType(type)
              .airbyteType(JsonSchemaType.INTEGER)
              .addInsertValues("null", "1001", "-2147483648", "2147483647")
              .addExpectedValues(null, "1001", "-2147483648", "2147483647")
              .build());
    }

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

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("money")
            .airbyteType(JsonSchemaType.NUMBER)
            .addInsertValues(
                "null",
                "'999.99'", "'1,001.01'", "'-1,000'",
                "'$999.99'", "'$1001.01'", "'-$1,000'"
            // max values for Money type: "-92233720368547758.08", "92233720368547758.07"
            // Debezium has wrong parsing for values more than 999999999999999 and less than -999999999999999
            // https://github.com/airbytehq/airbyte/issues/7338
            /* "'-92233720368547758.08'", "'92233720368547758.07'" */)
            .addExpectedValues(
                null,
                // Double#toString method is necessary here because sometimes the output
                // has unexpected decimals, e.g. Double.toString(-1000) is -1000.0
                "999.99", "1001.01", Double.toString(-1000),
                "999.99", "1001.01", Double.toString(-1000)
            /* "-92233720368547758.08", "92233720368547758.07" */)
            .build());

    // Blocked by https://github.com/airbytehq/airbyte/issues/8902
    for (final String type : Set.of("numeric", "decimal")) {
      addDataTypeTestData(
          TestDataHolder.builder()
              .sourceType(type)
              .airbyteType(JsonSchemaType.NUMBER)
              .addInsertValues(
                  "'123'", "null", "'1234567890.1234567'")
              // Postgres source does not support these special values yet
              // https://github.com/airbytehq/airbyte/issues/8902
              // "'infinity'", "'-infinity'", "'nan'"
              .addExpectedValues("123", null, "1.2345678901234567E9")
              .build());
    }

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("path")
            .airbyteType(JsonSchemaType.STRING)
            .addInsertValues("'((3,7),(15,18))'", "'((0,0),(0,0))'", "null")
            .addExpectedValues("((3.0,7.0),(15.0,18.0))", "((0.0,0.0),(0.0,0.0))", null)
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("pg_lsn")
            .airbyteType(JsonSchemaType.STRING)
            .addInsertValues("'7/A25801C8'::pg_lsn", "'0/0'::pg_lsn", "null")
            .addExpectedValues("7/A25801C8", "0/0", null)
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("point")
            .airbyteType(JsonSchemaType.STRING)
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

    for (final String type : Set.of("real", "float4")) {
      addDataTypeTestData(
          TestDataHolder.builder()
              .sourceType(type)
              .airbyteType(JsonSchemaType.NUMBER)
              .addInsertValues("null", "3.4145")
              .addExpectedValues(null, "3.4145")
              .build());
    }

    for (final String type : Set.of("smallint", "int2")) {
      addDataTypeTestData(
          TestDataHolder.builder()
              .sourceType(type)
              .airbyteType(JsonSchemaType.INTEGER)
              .addInsertValues("null", "-32768", "32767")
              .addExpectedValues(null, "-32768", "32767")
              .build());
    }

    for (final String type : Set.of("smallserial", "serial2")) {
      addDataTypeTestData(
          TestDataHolder.builder()
              .sourceType(type)
              .airbyteType(JsonSchemaType.INTEGER)
              .addInsertValues("1", "32767", "0", "-32767")
              .addExpectedValues("1", "32767", "0", "-32767")
              .build());
    }

    for (final String type : Set.of("serial", "serial4")) {
      addDataTypeTestData(
          TestDataHolder.builder()
              .sourceType(type)
              .airbyteType(JsonSchemaType.INTEGER)
              .addInsertValues("1", "2147483647", "0", "-2147483647")
              .addExpectedValues("1", "2147483647", "0", "-2147483647")
              .build());
    }

    // time without time zone
    for (final String fullSourceType : Set.of("time", "time without time zone", "time without time zone not null default now()")) {
      addDataTypeTestData(
          TestDataHolder.builder()
              .sourceType("time")
              .fullSourceDataType(fullSourceType)
              .airbyteType(JsonSchemaType.STRING_TIME_WITHOUT_TIMEZONE)
              // time column will ignore time zone
              .addInsertValues("'13:00:01'", "'13:00:02+8'", "'13:00:03-8'", "'13:00:04Z'", "'13:00:05.01234Z+8'", "'13:00:00Z-8'", "'24:00:00'")
              .addExpectedValues("13:00:01.000000", "13:00:02.000000", "13:00:03.000000", "13:00:04.000000", "13:00:05.012340",
                  "13:00:00.000000", "23:59:59.999999")
              .build());
    }

    // time without time zone
    for (final String fullSourceType : Set.of("time", "time without time zone")) {
      addDataTypeTestData(
          TestDataHolder.builder()
              .sourceType("time")
              .fullSourceDataType(fullSourceType)
              .airbyteType(JsonSchemaType.STRING_TIME_WITHOUT_TIMEZONE)
              // time column will ignore time zone
              .addInsertValues("null")
              .addExpectedValues((String) null)
              .build());
    }

    // timestamp without time zone
    for (final String fullSourceType : Set.of("timestamp", "timestamp without time zone", "timestamp without time zone default now()")) {
      addDataTypeTestData(
          TestDataHolder.builder()
              .sourceType("timestamp")
              .fullSourceDataType(fullSourceType)
              .airbyteType(JsonSchemaType.STRING_TIMESTAMP_WITHOUT_TIMEZONE)
              .addInsertValues(
                  "TIMESTAMP '2004-10-19 10:23:00'",
                  "TIMESTAMP '2004-10-19 10:23:54.123456'",
                  // A random BCE date. Old enough that converting it to/from an Instant results in discrepancies from
                  // inconsistent leap year handling
                  "TIMESTAMP '3004-10-19 10:23:54.123456 BC'",
                  // The earliest possible timestamp in CE
                  "TIMESTAMP '0001-01-01 00:00:00.000000'",
                  // The last possible timestamp in BCE
                  "TIMESTAMP '0001-12-31 23:59:59.999999 BC'",
                  "'epoch'")
              .addExpectedValues(
                  "2004-10-19T10:23:00.000000",
                  "2004-10-19T10:23:54.123456",
                  "3004-10-19T10:23:54.123456 BC",
                  "0001-01-01T00:00:00.000000",
                  "0001-12-31T23:59:59.999999 BC",
                  "1970-01-01T00:00:00.000000")
              .build());
    }

    // timestamp without time zone
    for (final String fullSourceType : Set.of("timestamp", "timestamp without time zone")) {
      addDataTypeTestData(
          TestDataHolder.builder()
              .sourceType("timestamp")
              .fullSourceDataType(fullSourceType)
              .airbyteType(JsonSchemaType.STRING_TIMESTAMP_WITHOUT_TIMEZONE)
              .addInsertValues("null")
              .addExpectedValues((String) null)
              .build());
    }

    addTimestampWithInfinityValuesTest();

    // timestamp with time zone
    for (final String fullSourceType : Set.of("timestamptz", "timestamp with time zone")) {
      addDataTypeTestData(
          TestDataHolder.builder()
              .sourceType("timestamptz")
              .fullSourceDataType(fullSourceType)
              .airbyteType(JsonSchemaType.STRING_TIMESTAMP_WITH_TIMEZONE)
              .addInsertValues(
                  // 10:23-08 == 18:23Z
                  "TIMESTAMP WITH TIME ZONE '2004-10-19 10:23:00-08'",
                  "TIMESTAMP WITH TIME ZONE '2004-10-19 10:23:54.123456-08'",
                  // A random BCE date. Old enough that converting it to/from an Instant results in discrepancies from
                  // inconsistent leap year handling
                  "TIMESTAMP WITH TIME ZONE '3004-10-19 10:23:54.123456-08 BC'",
                  // The earliest possible timestamp in CE (16:00-08 == 00:00Z)
                  "TIMESTAMP WITH TIME ZONE '0001-12-31 16:00:00.000000-08 BC'",
                  // The last possible timestamp in BCE (15:59-08 == 23:59Z)
                  "TIMESTAMP WITH TIME ZONE '0001-12-31 15:59:59.999999-08 BC'",
                  "null")
              .addExpectedValues(
                  "2004-10-19T18:23:00.000000Z",
                  "2004-10-19T18:23:54.123456Z",
                  "3004-10-19T18:23:54.123456Z BC",
                  "0001-01-01T00:00:00.000000Z",
                  "0001-12-31T23:59:59.999999Z BC",
                  null)
              .build());
    }

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("tsquery")
            .airbyteType(JsonSchemaType.STRING)
            .addInsertValues("null", "'fat & (rat | cat)'::tsquery", "'fat:ab & cat'::tsquery")
            .addExpectedValues(null, "'fat' & ( 'rat' | 'cat' )", "'fat':AB & 'cat'")
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

    // enum type
    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("mood")
            .airbyteType(JsonSchemaType.STRING)
            .addInsertValues("'happy'", "null")
            .addExpectedValues("happy", null)
            .build());

    // range
    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("tsrange")
            .airbyteType(JsonSchemaType.STRING)
            .addInsertValues("'(2010-01-01 14:30, 2010-01-01 15:30)'", "null")
            .addExpectedValues("(\"2010-01-01 14:30:00\",\"2010-01-01 15:30:00\")", null)
            .build());

    // composite type
    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("inventory_item")
            .airbyteType(JsonSchemaType.STRING)
            .addInsertValues("ROW('fuzzy dice', 42, 1.99)", "null")
            .addExpectedValues("(\"fuzzy dice\",42,1.99)", null)
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("hstore")
            .airbyteType(JsonSchemaType.STRING)
            .addInsertValues("""
                             '"paperback" => "243","publisher" => "postgresqltutorial.com",
                             "language"  => "English","ISBN-13" => "978-1449370000",
                             "weight"    => "11.2 ounces"'
                             """, null)
            .addExpectedValues(
                """
                {"ISBN-13":"978-1449370000","weight":"11.2 ounces","paperback":"243","publisher":"postgresqltutorial.com","language":"English"}""",
                null)
            .build());

    addTimeWithTimeZoneTest();
    addArraysTestData();
  }

  protected void addTimeWithTimeZoneTest() {
    // time with time zone
    for (final String fullSourceType : Set.of("timetz", "time with time zone")) {
      addDataTypeTestData(
          TestDataHolder.builder()
              .sourceType("timetz")
              .fullSourceDataType(fullSourceType)
              .airbyteType(JsonSchemaType.STRING_TIME_WITH_TIMEZONE)
              .addInsertValues("null", "'13:00:01'", "'13:00:00+8'", "'13:00:03-8'", "'13:00:04Z'", "'13:00:05.012345Z+8'", "'13:00:06.00000Z-8'")
              // A time value without time zone will use the time zone set on the database, which is Z-7,
              // so 13:00:01 is returned as 13:00:01-07.
              .addExpectedValues(null, "13:00:01.000000-07:00", "13:00:00.000000+08:00", "13:00:03.000000-08:00", "13:00:04.000000Z",
                  "13:00:05.012345-08:00", "13:00:06.000000+08:00")
              .build());
    }
  }

  protected void addTimestampWithInfinityValuesTest() {
    // timestamp without time zone
    for (final String fullSourceType : Set.of("timestamp", "timestamp without time zone", "timestamp without time zone not null default now()")) {
      addDataTypeTestData(
          TestDataHolder.builder()
              .sourceType("timestamp")
              .fullSourceDataType(fullSourceType)
              .airbyteType(JsonSchemaType.STRING_TIMESTAMP_WITHOUT_TIMEZONE)
              .addInsertValues(
                  "'infinity'",
                  "'-infinity'")
              .addExpectedValues(
                  "+292278994-08-16T23:00:00.000000",
                  "+292269055-12-02T23:00:00.000000 BC")
              .build());
    }
  }

  private void addArraysTestData() {
    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("int2_array")
            .fullSourceDataType("INT2[]")
            .airbyteType(JsonSchemaType.builder(JsonSchemaPrimitive.ARRAY)
                .withItems(JsonSchemaType.INTEGER)
                .build())
            .addInsertValues("'{1,2,3}'", "'{4,5,6}'")
            .addExpectedValues("[1,2,3]", "[4,5,6]")
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("int4_array")
            .fullSourceDataType("INT4[]")
            .airbyteType(JsonSchemaType.builder(JsonSchemaPrimitive.ARRAY)
                .withItems(JsonSchemaType.INTEGER)
                .build())
            .addInsertValues("'{-2147483648,2147483646}'")
            .addExpectedValues("[-2147483648,2147483646]")
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("int8_array")
            .fullSourceDataType("INT8[]")
            .airbyteType(JsonSchemaType.builder(JsonSchemaPrimitive.ARRAY)
                .withItems(JsonSchemaType.INTEGER)
                .build())
            .addInsertValues("'{-9223372036854775808,9223372036854775801}'")
            .addExpectedValues("[-9223372036854775808,9223372036854775801]")
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("oid_array")
            .fullSourceDataType("OID[]")
            .airbyteType(JsonSchemaType.builder(JsonSchemaPrimitive.ARRAY)
                .withItems(JsonSchemaType.builder(JsonSchemaPrimitive.NUMBER)
                    .build())
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
                .build())
            .addInsertValues("'{l,d,a}'")
            .addExpectedValues("[\"l\",\"d\",\"a\"]")
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("bpchar_array")
            .fullSourceDataType("BPCHAR(2)[]")
            .airbyteType(JsonSchemaType.builder(JsonSchemaPrimitive.ARRAY)
                .withItems(JsonSchemaType.builder(JsonSchemaPrimitive.STRING)
                    .build())
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
                .build())
            .addInsertValues("'{$999.99,$1001.01,45000, $1.001,$800,22222.006, 1001.01}'")
            .addExpectedValues("[999.99,1001.01,45000.0,1.0,800.0,22222.01,1001.01]")
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("bool_array")
            .fullSourceDataType("BOOL[]")
            .airbyteType(JsonSchemaType.builder(JsonSchemaPrimitive.ARRAY)
                .withItems(JsonSchemaType.builder(JsonSchemaPrimitive.BOOLEAN)
                    .build())
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
                .build())
            .addInsertValues(
                "'{\\xA6697E974E6A320F454390BE03F74955E8978F1A6971EA6730542E37B66179BC,\\x4B52414B00000000000000000000000000000000000000000000000000000000}'")
            .addExpectedValues(
                "[\"eEE2Njk3RTk3NEU2QTMyMEY0NTQzOTBCRTAzRjc0OTU1RTg5NzhGMUE2OTcxRUE2NzMwNTQyRTM3QjY2MTc5QkM=\",\"eDRCNTI0MTRCMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDA=\"]")
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("date_array")
            .fullSourceDataType("DATE[]")
            .airbyteType(JsonSchemaType.builder(JsonSchemaPrimitive.ARRAY)
                .withItems(STRING_DATE)
                .build())
            .addInsertValues("'{1999-01-08,1991-02-10 BC}'")
            .addExpectedValues("[\"1999-01-08\",\"1991-02-10 BC\"]")
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("time_array")
            .fullSourceDataType("TIME(6)[]")
            .airbyteType(JsonSchemaType.builder(JsonSchemaPrimitive.ARRAY)
                .withItems(STRING_TIME_WITHOUT_TIMEZONE)
                .build())
            .addInsertValues("'{13:00:01,13:00:02+8,13:00:03-8,13:00:04Z,13:00:05.000000+8,13:00:00Z-8}'")
            .addExpectedValues(
                "[\"13:00:01.000000\",\"13:00:02.000000\",\"13:00:03.000000\",\"13:00:04.000000\",\"13:00:05.000000\",\"13:00:00.000000\"]")
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("timetz_array")
            .fullSourceDataType("TIMETZ[]")
            .airbyteType(JsonSchemaType.builder(JsonSchemaPrimitive.ARRAY)
                .withItems(STRING_TIME_WITH_TIMEZONE)
                .build())
            .addInsertValues("'{null,13:00:01,13:00:00+8,13:00:03-8,13:00:04Z,13:00:05.012345Z+8,13:00:06.00000Z-8,13:00}'")
            .addExpectedValues(
                "[null,\"13:00:01.000000-07:00\",\"13:00:00.000000+08:00\",\"13:00:03.000000-08:00\",\"13:00:04.000000Z\",\"13:00:05.012345-08:00\",\"13:00:06.000000+08:00\",\"13:00:00.000000-07:00\"]")
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("timestamptz_array")
            .fullSourceDataType("TIMESTAMPTZ[]")
            .airbyteType(JsonSchemaType.builder(JsonSchemaPrimitive.ARRAY)
                .withItems(STRING_TIMESTAMP_WITH_TIMEZONE)
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
                .build())
            .addInsertValues("'{null,2004-10-19 10:23:00,2004-10-19 10:23:54.123456,3004-10-19 10:23:54.123456 BC}'")
            .addExpectedValues("[null,\"2004-10-19T10:23:00.000000\",\"2004-10-19T10:23:54.123456\",\"3004-10-19T10:23:54.123456 BC\"]")
            .build());
  }

}
