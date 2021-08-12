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
    final JsonNode replicationMethod = Jsons.jsonNode(ImmutableMap.builder()
        .put("method", "Standard")
        .build());
    config = Jsons.jsonNode(ImmutableMap.builder()
        .put("host", container.getHost())
        .put("port", container.getFirstMappedPort())
        .put("database", container.getDatabaseName())
        .put("username", container.getUsername())
        .put("password", container.getPassword())
        .put("ssl", false)
        .put("replication_method", replicationMethod)
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
    database.query(ctx -> ctx.fetch("CREATE TYPE mood AS ENUM ('sad', 'ok', 'happy');"));
    database.query(ctx -> ctx.fetch("CREATE TYPE inventory_item AS (\n"
        + "    name            text,\n"
        + "    supplier_id     integer,\n"
        + "    price           numeric\n"
        + ");"));

    return database;
  }

  @Override
  protected String getNameSpace() {
    return "test";
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
            .airbyteType(JsonSchemaPrimitive.NUMBER)
            .addInsertValues("-9223372036854775808", "9223372036854775807", "0", "null")
            .addExpectedValues("-9223372036854775808", "9223372036854775807", "0", null)
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("bigserial")
            .airbyteType(JsonSchemaPrimitive.NUMBER)
            .addInsertValues("1", "9223372036854775807", "0", "-9223372036854775808")
            .addExpectedValues("1", "9223372036854775807", "0", "-9223372036854775808")
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("serial")
            .airbyteType(JsonSchemaPrimitive.NUMBER)
            .addInsertValues("1", "2147483647", "0", "-2147483647")
            .addExpectedValues("1", "2147483647", "0", "-2147483647")
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("smallserial")
            .airbyteType(JsonSchemaPrimitive.NUMBER)
            .addInsertValues("1", "32767", "0", "-32767")
            .addExpectedValues("1", "32767", "0", "-32767")
            .build());

    // BUG https://github.com/airbytehq/airbyte/issues/3932
    // BIT type is currently parsed as a Boolean which is incorrect
    // addDataTypeTestData(
    // TestDataHolder.builder()
    // .sourceType("bit")
    // .fullSourceDataType("BIT(3)")
    // .airbyteType(JsonSchemaPrimitive.NUMBER)
    // .addInsertValues("B'101'")
    // //.addExpectedValues("101")
    // - .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("bit_varying")
            .fullSourceDataType("BIT VARYING(5)")
            .airbyteType(JsonSchemaPrimitive.NUMBER)
            .addInsertValues("B'101'", "null")
            .addExpectedValues("101", null)
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("boolean")
            .airbyteType(JsonSchemaPrimitive.BOOLEAN)
            .addInsertValues("true", "'yes'", "'1'", "false", "'no'", "'0'", "null")
            .addExpectedValues("true", "true", "true", "false", "false", "false", null)
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("bytea")
            .airbyteType(JsonSchemaPrimitive.OBJECT)
            .addInsertValues("decode('1234', 'hex')")
            .addExpectedValues("EjQ=")
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("character")
            .airbyteType(JsonSchemaPrimitive.STRING)
            .addInsertValues("'a'", "'*'", "null")
            .addExpectedValues("a", "*", null)
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("character")
            .fullSourceDataType("character(8)")
            .airbyteType(JsonSchemaPrimitive.STRING)
            .addInsertValues("'{asb123}'", "'{asb12}'")
            .addExpectedValues("{asb123}", "{asb12} ")
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("varchar")
            .airbyteType(JsonSchemaPrimitive.STRING)
            .addInsertValues("'a'", "'abc'", "'Миші йдуть на південь, не питай чому;'", "'櫻花分店'",
                "''", "null", "'\\xF0\\x9F\\x9A\\x80'")
            .addExpectedValues("a", "abc", "Миші йдуть на південь, не питай чому;", "櫻花分店", "",
                null, "\\xF0\\x9F\\x9A\\x80")
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("varchar")
            .fullSourceDataType("character(12)")
            .airbyteType(JsonSchemaPrimitive.STRING)
            .addInsertValues("'a'", "'abc'", "'Миші йдуть;'", "'櫻花分店'",
                "''", "null")
            .addExpectedValues("a           ", "abc         ", "Миші йдуть; ", "櫻花分店        ",
                "            ", null)
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("cidr")
            .airbyteType(JsonSchemaPrimitive.STRING)
            .addInsertValues("null", "'192.168.100.128/25'", "'192.168/24'", "'192.168.1'",
                "'128.1'", "'2001:4f8:3:ba::/64'")
            .addExpectedValues(null, "192.168.100.128/25", "192.168.0.0/24", "192.168.1.0/24",
                "128.1.0.0/16", "2001:4f8:3:ba::/64")
            .build());

    // JdbcUtils-> DATE_FORMAT is set as ""yyyy-MM-dd'T'HH:mm:ss'Z'"" so it doesnt suppose to handle BC
    // dates
    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("date")
            .airbyteType(JsonSchemaPrimitive.STRING)
            .addInsertValues("'1999-01-08'", "null") // "'199-10-10 BC'"
            .addExpectedValues("1999-01-08T00:00:00Z", null) // , "199-10-10 BC")
            .build());

    // Values "'-Infinity'", "'Infinity'", "'Nan'" will not be parsed due to:
    // JdbcUtils -> setJsonField contains:
    // case FLOAT, DOUBLE -> o.put(columnName, nullIfInvalid(() -> r.getDouble(i), Double::isFinite));
    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("float8")
            .airbyteType(JsonSchemaPrimitive.NUMBER)
            .addInsertValues("'123'", "'1234567890.1234567'", "null")
            .addExpectedValues("123.0", "1.2345678901234567E9", null)
            .build());

    // Values "'-Infinity'", "'Infinity'", "'Nan'" will not be parsed due to:
    // JdbcUtils -> setJsonField contains:
    // case FLOAT, DOUBLE -> o.put(columnName, nullIfInvalid(() -> r.getDouble(i), Double::isFinite));
    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("float")
            .airbyteType(JsonSchemaPrimitive.NUMBER)
            .addInsertValues("'123'", "'1234567890.1234567'", "null")
            .addExpectedValues("123.0", "1.2345678901234567E9", null)
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("inet")
            .airbyteType(JsonSchemaPrimitive.STRING)
            .addInsertValues("'198.24.10.0/24'", "'198.24.10.0'", "'198.10/8'", "null")
            .addExpectedValues("198.24.10.0/24", "198.24.10.0", "198.10.0.0/8", null)
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
            .sourceType("interval")
            .airbyteType(JsonSchemaPrimitive.STRING)
            .addInsertValues("null", "'P1Y2M3DT4H5M6S'", "'-178000000'", "'178000000'")
            .addExpectedValues(null, "1 year 2 mons 3 days 04:05:06", "-49444:26:40", "49444:26:40")
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("json")
            .airbyteType(JsonSchemaPrimitive.STRING)
            .addInsertValues("null", "'{\"a\": 10, \"b\": 15}'")
            .addExpectedValues(null, "{\"a\": 10, \"b\": 15}")
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("jsonb")
            .airbyteType(JsonSchemaPrimitive.STRING)
            .addInsertValues("null", "'[1, 2, 3]'::jsonb")
            .addExpectedValues(null, "[1, 2, 3]")
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("macaddr")
            .airbyteType(JsonSchemaPrimitive.STRING)
            .addInsertValues("null", "'08:00:2b:01:02:03'", "'08-00-2b-01-02-04'",
                "'08002b:010205'")
            .addExpectedValues(null, "08:00:2b:01:02:03", "08:00:2b:01:02:04", "08:00:2b:01:02:05")
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("macaddr8")
            .airbyteType(JsonSchemaPrimitive.STRING)
            .addInsertValues("null", "'08:00:2b:01:02:03:04:05'", "'08-00-2b-01-02-03-04-06'",
                "'08002b:0102030407'")
            .addExpectedValues(null, "08:00:2b:01:02:03:04:05", "08:00:2b:01:02:03:04:06",
                "08:00:2b:01:02:03:04:07")
            .build());

    // The Money type fails when amount is > 1,000. in JdbcUtils-> rowToJson as r.getObject(i);
    // Bad value for type double : 1,000.01
    // The reason is that in jdbc implementation money type is tried to get as Double (jdbc
    // implementation)
    // Max values for Money type: "-92233720368547758.08", "92233720368547758.07"
    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("money")
            .airbyteType(JsonSchemaPrimitive.STRING)
            .addInsertValues("null", "'999.99'")
            .addExpectedValues(null, "999.99")
            .build());

    // The numeric type in Postres may contain 'Nan' type, but in JdbcUtils-> rowToJson
    // we try to map it like this, so it fails
    // case NUMERIC, DECIMAL -> o.put(columnName, nullIfInvalid(() -> r.getBigDecimal(i)));
    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("numeric")
            .airbyteType(JsonSchemaPrimitive.NUMBER)
            .addInsertValues("'99999'", "null")
            .addExpectedValues("99999", null)
            .build());

    // The numeric type in Postres may contain 'Nan' type, but in JdbcUtils-> rowToJson
    // we try to map it like this, so it fails
    // case NUMERIC, DECIMAL -> o.put(columnName, nullIfInvalid(() -> r.getBigDecimal(i)));
    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("decimal")
            .airbyteType(JsonSchemaPrimitive.NUMBER)
            .addInsertValues("99999", "5.1", "0", "null")
            .addExpectedValues("99999", "5.1", "0", null)
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
            .sourceType("text")
            .airbyteType(JsonSchemaPrimitive.STRING)
            .addInsertValues("'a'", "'abc'", "'Миші йдуть;'", "'櫻花分店'",
                "''", "null", "'\\xF0\\x9F\\x9A\\x80'")
            .addExpectedValues("a", "abc", "Миші йдуть;", "櫻花分店", "", null, "\\xF0\\x9F\\x9A\\x80")
            .build());

    // JdbcUtils-> DATE_FORMAT is set as ""yyyy-MM-dd'T'HH:mm:ss'Z'"" for both Date and Time types.
    // So Time only (04:05:06) would be represented like "1970-01-01T04:05:06Z" which is incorrect
    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("time")
            .airbyteType(JsonSchemaPrimitive.STRING)
            .addInsertValues("null")
            .addNullExpectedValue()
            .build());

    // JdbcUtils-> DATE_FORMAT is set as ""yyyy-MM-dd'T'HH:mm:ss'Z'"" for both Date and Time types.
    // So Time only (04:05:06) would be represented like "1970-01-01T04:05:06Z" which is incorrect
    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("timetz")
            .airbyteType(JsonSchemaPrimitive.STRING)
            .addInsertValues("null")
            .addNullExpectedValue()
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("timestamp")
            .airbyteType(JsonSchemaPrimitive.STRING)
            .addInsertValues("TIMESTAMP '2004-10-19 10:23:54'", "null")
            .addExpectedValues("2004-10-19T10:23:54Z", null)
            .build());

    // May be run locally, but correct the timezone aacording to your location
    // addDataTypeTestData(
    // TestDataHolder.builder()
    // .sourceType("timestamptz")
    // .airbyteType(JsonSchemaPrimitive.STRING)
    // .addInsertValues("TIMESTAMP '2004-10-19 10:23:54+02'", "null")
    // .addExpectedValues("2004-10-19T07:23:54Z", null)
    // .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("tsvector")
            .airbyteType(JsonSchemaPrimitive.STRING)
            .addInsertValues("to_tsvector('The quick brown fox jumped over the lazy dog.')")
            .addExpectedValues("'brown':3 'dog':9 'fox':4 'jump':5 'lazi':8 'quick':2")
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("uuid")
            .airbyteType(JsonSchemaPrimitive.STRING)
            .addInsertValues("'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11'", "null")
            .addExpectedValues("a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11", null)
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("xml")
            .airbyteType(JsonSchemaPrimitive.STRING)
            .addInsertValues(
                "XMLPARSE (DOCUMENT '<?xml version=\"1.0\"?><book><title>Manual</title><chapter>...</chapter></book>')",
                "null", "''")
            .addExpectedValues("<book><title>Manual</title><chapter>...</chapter></book>", null, "")
            .build());

    // preconditions for this test are set at the time of database creation (setupDatabase method)
    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("mood")
            .airbyteType(JsonSchemaPrimitive.STRING)
            .addInsertValues("'happy'", "null")
            .addExpectedValues("happy", null)
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("text")
            .fullSourceDataType("text[]")
            .airbyteType(JsonSchemaPrimitive.STRING)
            .addInsertValues("'{10000, 10000, 10000, 10000}'", "null")
            .addExpectedValues("{10000,10000,10000,10000}", null)
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("inventory_item")
            .airbyteType(JsonSchemaPrimitive.STRING)
            .addInsertValues("ROW('fuzzy dice', 42, 1.99)", "null")
            .addExpectedValues("(\"fuzzy dice\",42,1.99)", null)
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("tsrange")
            .airbyteType(JsonSchemaPrimitive.STRING)
            .addInsertValues("'(2010-01-01 14:30, 2010-01-01 15:30)'", "null")
            .addExpectedValues("(\"2010-01-01 14:30:00\",\"2010-01-01 15:30:00\")", null)
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("box")
            .airbyteType(JsonSchemaPrimitive.STRING)
            .addInsertValues("'((3,7),(15,18))'", "'((0,0),(0,0))'", "null")
            .addExpectedValues("(15,18),(3,7)", "(0,0),(0,0)", null)
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("circle")
            .airbyteType(JsonSchemaPrimitive.STRING)
            .addInsertValues("'(5,7),10'", "'(0,0),0'", "'(-10,-4),10'", "null")
            .addExpectedValues("<(5,7),10>", "<(0,0),0>", "<(-10,-4),10>", null)
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("line")
            .airbyteType(JsonSchemaPrimitive.STRING)
            .addInsertValues("'{4,5,6}'", "'{0,1,0}'", "null")
            .addExpectedValues("{4,5,6}", "{0,1,0}", null)
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("lseg")
            .airbyteType(JsonSchemaPrimitive.STRING)
            .addInsertValues("'((3,7),(15,18))'", "'((0,0),(0,0))'", "null")
            .addExpectedValues("[(3,7),(15,18)]", "[(0,0),(0,0)]", null)
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("path")
            .airbyteType(JsonSchemaPrimitive.STRING)
            .addInsertValues("'((3,7),(15,18))'", "'((0,0),(0,0))'", "null")
            .addExpectedValues("((3,7),(15,18))", "((0,0),(0,0))", null)
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("point")
            .airbyteType(JsonSchemaPrimitive.NUMBER)
            .addInsertValues("'(3,7)'", "'(0,0)'", "'(999999999999999999999999,0)'", "null")
            .addExpectedValues("(3,7)", "(0,0)", "(1e+24,0)", null)
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("polygon")
            .airbyteType(JsonSchemaPrimitive.STRING)
            .addInsertValues("'((3,7),(15,18))'", "'((0,0),(0,0))'",
                "'((0,0),(999999999999999999999999,0))'", "null")
            .addExpectedValues("((3,7),(15,18))", "((0,0),(0,0))", "((0,0),(1e+24,0))", null)
            .build());
  }

}
