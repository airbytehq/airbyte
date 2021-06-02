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
import io.airbyte.integrations.standardtest.source.SourceComprehensiveTest;
import io.airbyte.integrations.standardtest.source.TestDataWrapper;
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
  protected void initTests() {
    addDataTypeTestData(
        TestDataWrapper.builder("tinyint", JsonSchemaPrimitive.NUMBER)
            .addInsertValues("null")
            .addInsertValues("-128", "127")
            .build());

    addDataTypeTestData(
        TestDataWrapper.builder("smallint", JsonSchemaPrimitive.NUMBER)
            .addInsertValues("null")
            .addInsertValues("-32768", "32767")
            .build());

    addDataTypeTestData(
        TestDataWrapper.builder("smallint", JsonSchemaPrimitive.NUMBER)
            .fullSourceDataType("smallint zerofill")
            .addInsertValues("1")
            .build());

    addDataTypeTestData(
        TestDataWrapper.builder("mediumint", JsonSchemaPrimitive.NUMBER)
            .addInsertValues("null", "-8388608", "8388607")
            .build());

    addDataTypeTestData(
        TestDataWrapper.builder("mediumint", JsonSchemaPrimitive.NUMBER)
            .fullSourceDataType("mediumint zerofill")
            .addInsertValues("1")
            .build());

    addDataTypeTestData(
        TestDataWrapper.builder("int", JsonSchemaPrimitive.NUMBER)
            .addInsertValues("null", "-2147483648", "2147483647")
            .build());

    addDataTypeTestData(
        TestDataWrapper.builder("int", JsonSchemaPrimitive.NUMBER)
            .fullSourceDataType("int zerofill")
            .addInsertValues("1")
            .build());

    addDataTypeTestData(
        TestDataWrapper.builder("bigint", JsonSchemaPrimitive.NUMBER)
            .addInsertValues("null", "9223372036854775807")
            .build());

    addDataTypeTestData(
        TestDataWrapper.builder("float", JsonSchemaPrimitive.NUMBER)
            .addInsertValues("null")
            .build());

    addDataTypeTestData(
        TestDataWrapper.builder("double", JsonSchemaPrimitive.NUMBER)
            .addInsertValues("null", "power(10, 308)", "1/power(10, 45)")
            .build());

    addDataTypeTestData(
        TestDataWrapper.builder("decimal", JsonSchemaPrimitive.NUMBER)
            .fullSourceDataType("decimal(5,2)")
            .addInsertValues("null")
            .build());

    addDataTypeTestData(
        TestDataWrapper.builder("bit", JsonSchemaPrimitive.NUMBER)
            .addInsertValues("null", "1", "0")
            .build());

    addDataTypeTestData(
        TestDataWrapper.builder("date", JsonSchemaPrimitive.STRING)
            .addInsertValues("null")
            // .addInsertValue("'2021-01-00'")
            // .addInsertValue("'2021-00-00'")
            // .addInsertValue("'0000-00-00'")
            .build());

    addDataTypeTestData(
        TestDataWrapper.builder("datetime", JsonSchemaPrimitive.STRING)
            .addInsertValues("null")
            // .addInsertValue("'0000-00-00 00:00:00'")
            .build());

    addDataTypeTestData(
        TestDataWrapper.builder("timestamp", JsonSchemaPrimitive.STRING)
            .addInsertValues("null")
            .build());

    addDataTypeTestData(
        TestDataWrapper.builder("time", JsonSchemaPrimitive.STRING)
            .addInsertValues("null")
            // .addInsertValue("'-838:59:59.000000'")
            .build());

    addDataTypeTestData(
        TestDataWrapper.builder("varchar", JsonSchemaPrimitive.STRING)
            .fullSourceDataType("varchar(256) character set cp1251")
            .addInsertValues("null", "'тест'")
            .build());

    addDataTypeTestData(
        TestDataWrapper.builder("varchar", JsonSchemaPrimitive.STRING)
            .fullSourceDataType("varchar(256) character set utf16")
            .addInsertValues("null", "0xfffd")
            .build());

    addDataTypeTestData(
        TestDataWrapper.builder("varchar", JsonSchemaPrimitive.STRING)
            .fullSourceDataType("varchar(256)")
            .addInsertValues("null", "'!\"#$%&\\'()*+,-./:;<=>?\\@[\\]^_\\`{|}~'")
            .build());

    addDataTypeTestData(
        TestDataWrapper.builder("varbinary", JsonSchemaPrimitive.STRING)
            .fullSourceDataType("varbinary(256)")
            .addInsertValues("null", "'test'")
            .build());

    addDataTypeTestData(
        TestDataWrapper.builder("blob", JsonSchemaPrimitive.STRING)
            .addInsertValues("null", "'test'")
            .build());

    addDataTypeTestData(
        TestDataWrapper.builder("mediumtext", JsonSchemaPrimitive.STRING)
            .addInsertValues("null", "lpad('0', 16777214, '0')")
            .build());

    addDataTypeTestData(
        TestDataWrapper.builder("tinytext", JsonSchemaPrimitive.STRING)
            .addInsertValues("null")
            .build());

    addDataTypeTestData(
        TestDataWrapper.builder("longtext", JsonSchemaPrimitive.STRING)
            .addInsertValues("null")
            .build());

    addDataTypeTestData(
        TestDataWrapper.builder("text", JsonSchemaPrimitive.STRING)
            .addInsertValues("null")
            .build());

    addDataTypeTestData(
        TestDataWrapper.builder("json", JsonSchemaPrimitive.STRING)
            .addInsertValues("null", "'{\"a\" :10, \"b\": 15}'")
            .build());

    addDataTypeTestData(
        TestDataWrapper.builder("point", JsonSchemaPrimitive.OBJECT)
            .addInsertValues("null", "(ST_GeomFromText('POINT(1 1)'))")
            .build());

    addDataTypeTestData(
        TestDataWrapper.builder("bool", JsonSchemaPrimitive.STRING)
            .addInsertValues("null", "127", "-128")
            .build());

  }

}
