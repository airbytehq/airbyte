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

package io.airbyte.integrations.source.mysql;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.Database;
import io.airbyte.db.Databases;
import io.airbyte.integrations.source.mysql.MySqlSource.ReplicationMethod;
import io.airbyte.integrations.standardtest.source.SourceComprehensiveTest;
import io.airbyte.integrations.standardtest.source.TestDataHolder;
import io.airbyte.integrations.standardtest.source.TestDestinationEnv;
import io.airbyte.protocol.models.JsonSchemaPrimitive;
import org.jooq.SQLDialect;
import org.testcontainers.containers.MySQLContainer;

public class MySqlSourceComprehensiveTest extends SourceComprehensiveTest {

  private MySQLContainer<?> container;
  private JsonNode config;

  @Override
  protected JsonNode getConfig() {
    return config;
  }

  @Override
  protected void tearDown(TestDestinationEnv testEnv) {
    container.close();
  }

  @Override
  protected String getImageName() {
    return "airbyte/source-mysql:dev";
  }

  @Override
  protected Database setupDatabase() throws Exception {
    container = new MySQLContainer<>("mysql:8.0");
    container.start();

    config = Jsons.jsonNode(ImmutableMap.builder()
        .put("host", container.getHost())
        .put("port", container.getFirstMappedPort())
        .put("database", container.getDatabaseName())
        .put("username", container.getUsername())
        .put("password", container.getPassword())
        .put("replication_method", ReplicationMethod.STANDARD)
        .build());

    final Database database = Databases.createDatabase(
        config.get("username").asText(),
        config.get("password").asText(),
        String.format("jdbc:mysql://%s:%s/%s",
            config.get("host").asText(),
            config.get("port").asText(),
            config.get("database").asText()),
        "com.mysql.cj.jdbc.Driver",
        SQLDialect.MYSQL);

    // It disable strict mode in the DB and allows to insert specific values.
    // For example, it's possible to insert date with zero values "2021-00-00"
    database.query(ctx -> ctx.fetch("SET @@sql_mode=''"));

    return database;
  }

  @Override
  protected String getNameSpace() {
    return container.getDatabaseName();
  }

  @Override
  protected void initTests() {
    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("tinyint")
            .airbyteType(JsonSchemaPrimitive.NUMBER)
            .addInsertValues("null", "-128", "127")
            .addExpectedValues(null, "-128", "127")
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
            .sourceType("smallint")
            .airbyteType(JsonSchemaPrimitive.NUMBER)
            .fullSourceDataType("smallint zerofill")
            .addInsertValues("1")
            .addExpectedValues("1")
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("mediumint")
            .airbyteType(JsonSchemaPrimitive.NUMBER)
            .addInsertValues("null", "-8388608", "8388607")
            .addExpectedValues(null, "-8388608", "8388607")
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("mediumint")
            .airbyteType(JsonSchemaPrimitive.NUMBER)
            .fullSourceDataType("mediumint zerofill")
            .addInsertValues("1")
            .addExpectedValues("1")
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
            .sourceType("int")
            .airbyteType(JsonSchemaPrimitive.NUMBER)
            .fullSourceDataType("int unsigned")
            .addInsertValues("3428724653")
            .addExpectedValues("3428724653")
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("int")
            .airbyteType(JsonSchemaPrimitive.NUMBER)
            .fullSourceDataType("int zerofill")
            .addInsertValues("1")
            .addExpectedValues("1")
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("bigint")
            .airbyteType(JsonSchemaPrimitive.NUMBER)
            .addInsertValues("null", "9223372036854775807")
            .addExpectedValues(null, "9223372036854775807")
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("float")
            .airbyteType(JsonSchemaPrimitive.NUMBER)
            .addInsertValues("null")
            .addNullExpectedValue()
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("double")
            .airbyteType(JsonSchemaPrimitive.NUMBER)
            .addInsertValues("null", "power(10, 308)", "1/power(10, 45)")
            .addExpectedValues(null, String.valueOf(Math.pow(10, 308)), String.valueOf(1 / Math.pow(10, 45)))
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("decimal")
            .airbyteType(JsonSchemaPrimitive.NUMBER)
            .fullSourceDataType("decimal(10,4)")
            .addInsertValues("0.188", "null")
            .addExpectedValues("0.188", null)
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("decimal")
            .airbyteType(JsonSchemaPrimitive.NUMBER)
            .fullSourceDataType("decimal(19,2)")
            .addInsertValues("1700000.00")
            .addInsertValues("1700000.00")
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("bit")
            .airbyteType(JsonSchemaPrimitive.NUMBER)
            .addInsertValues("null", "1", "0")
            // @TODO returns True/False instead of 1/0.
            // .addExpectedValues(null, "1", "0")
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("date")
            .airbyteType(JsonSchemaPrimitive.STRING)
            .addInsertValues("null")
            .addNullExpectedValue()
            // @TODO stream fails when gets Zero date value
            // .addInsertValues("'2021-01-00'", "'2021-00-00'", "'0000-00-00'")
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("datetime")
            .airbyteType(JsonSchemaPrimitive.STRING)
            .addInsertValues("null")
            .addNullExpectedValue()
            // @TODO stream fails when gets Zero date value
            // .addInsertValues("'0000-00-00 00:00:00'")
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("timestamp")
            .airbyteType(JsonSchemaPrimitive.STRING)
            .addInsertValues("null")
            .addNullExpectedValue()
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("time")
            .airbyteType(JsonSchemaPrimitive.STRING)
            .addInsertValues("null")
            .addNullExpectedValue()
            // @TODO stream fails when gets Zero date value
            // .addInsertValues("'-838:59:59.000000'")
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("varchar")
            .airbyteType(JsonSchemaPrimitive.STRING)
            .fullSourceDataType("varchar(256) character set cp1251")
            .addInsertValues("null", "'тест'")
            .addExpectedValues(null, "тест")
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("varchar")
            .airbyteType(JsonSchemaPrimitive.STRING)
            .fullSourceDataType("varchar(256) character set utf16")
            .addInsertValues("null", "0xfffd")
            .addExpectedValues(null, "�")
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("varchar")
            .airbyteType(JsonSchemaPrimitive.STRING)
            .fullSourceDataType("varchar(256)")
            .addInsertValues("null", "'!\"#$%&\\'()*+,-./:;<=>?\\@[\\]^_\\`{|}~'")
            .addExpectedValues(null, "!\"#$%&'()*+,-./:;<=>?@[]^_`{|}~")
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("varbinary")
            .airbyteType(JsonSchemaPrimitive.STRING)
            .fullSourceDataType("varbinary(256)")
            .addInsertValues("null", "'test'")
            // @TODO Returns binary value instead of text
            // .addExpectedValues(null, "test")
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("blob")
            .airbyteType(JsonSchemaPrimitive.STRING)
            .addInsertValues("null", "'test'")
            // @TODO Returns binary value instead of text
            // .addExpectedValues(null, "test")
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("mediumtext")
            .airbyteType(JsonSchemaPrimitive.STRING)
            .addInsertValues("null", "lpad('0', 16777214, '0')")
            // @TODO returns null instead of long text
            // .addExpectedValues(null, StringUtils.leftPad("0", 16777214, "0"))
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("tinytext")
            .airbyteType(JsonSchemaPrimitive.STRING)
            .addInsertValues("null")
            .addNullExpectedValue()
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("longtext")
            .airbyteType(JsonSchemaPrimitive.STRING)
            .addInsertValues("null")
            .addNullExpectedValue()
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("text")
            .airbyteType(JsonSchemaPrimitive.STRING)
            .addInsertValues("null")
            .addNullExpectedValue()
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
            .sourceType("point")
            .airbyteType(JsonSchemaPrimitive.OBJECT)
            .addInsertValues("null", "(ST_GeomFromText('POINT(1 1)'))")
            .build());

    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("bool")
            .airbyteType(JsonSchemaPrimitive.STRING)
            .addInsertValues("null", "1", "127", "-128")
            // @TODO in MySQL boolean returns true only if value equals 1, all other not null values -> false
            // .addExpectedValues(null, "true", "false", "false")
            .build());

  }

}
