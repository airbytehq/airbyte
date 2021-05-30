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
import io.airbyte.protocol.models.Field.JsonSchemaPrimitive;
import org.jooq.SQLDialect;
import org.testcontainers.containers.MySQLContainer;

public class MySqlSourceComprehensiveTest extends SourceComprehensiveTest {

  private MySQLContainer<?> container;
  private JsonNode config;

  @Override
  protected JsonNode setupConfig(TestDestinationEnv testEnv) {
    container = new MySQLContainer<>("mysql:8.0");
    container.start();

    config = Jsons.jsonNode(ImmutableMap.builder()
        .put("host", container.getHost())
        .put("port", container.getFirstMappedPort())
        .put("database", container.getDatabaseName())
        .put("username", container.getUsername())
        .put("password", container.getPassword())
        .build());

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
  protected Database setupDatabase(JsonNode config) throws Exception {
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
    addDataTypeTest(
            new DataTypeTest("tinyint", JsonSchemaPrimitive.NUMBER)
                    .addInsertValue("null")
                    .addInsertValue("-128")
                    .addInsertValue("127")
    );
    addDataTypeTest(
            new DataTypeTest("smallint", JsonSchemaPrimitive.NUMBER)
                    .addInsertValue("null")
                    .addInsertValue("-32768")
                    .addInsertValue("32767")
    );

    addDataTypeTest(
            new DataTypeTest("smallint", JsonSchemaPrimitive.NUMBER)
                    .setFullSourceDataType("smallint zerofill")
                    .addInsertValue("1")
    );

    addDataTypeTest(
            new DataTypeTest("mediumint", JsonSchemaPrimitive.NUMBER)
                    .addInsertValue("null")
                    .addInsertValue("-8388608")
                    .addInsertValue("8388607")
    );

    addDataTypeTest(
            new DataTypeTest("mediumint", JsonSchemaPrimitive.NUMBER)
                    .setFullSourceDataType("mediumint zerofill")
                    .addInsertValue("1")
    );

    addDataTypeTest(
            new DataTypeTest("int", JsonSchemaPrimitive.NUMBER)
                    .addInsertValue("null")
                    .addInsertValue("-2147483648")
                    .addInsertValue("2147483647")
    );

    addDataTypeTest(
            new DataTypeTest("int", JsonSchemaPrimitive.NUMBER)
                    .setFullSourceDataType("int zerofill")
                    .addInsertValue("1")
    );

    addDataTypeTest(
            new DataTypeTest("bigint", JsonSchemaPrimitive.NUMBER)
                    .addInsertValue("null")
                    .addInsertValue("9223372036854775807")
    );

    addDataTypeTest(
            new DataTypeTest("float", JsonSchemaPrimitive.NUMBER)
                    .addInsertValue("null")
    );

    addDataTypeTest(
            new DataTypeTest("double", JsonSchemaPrimitive.NUMBER)
                    .addInsertValue("null")
                    .addInsertValue("power(10, 308)")
                    .addInsertValue("1/power(10, 45)")
    );

    addDataTypeTest(
            new DataTypeTest("decimal", JsonSchemaPrimitive.NUMBER)
                    .setFullSourceDataType("decimal(5,2)")
                    .addInsertValue("null")
    );

    addDataTypeTest(
            new DataTypeTest("bit", JsonSchemaPrimitive.NUMBER)
                    .addInsertValue("null")
                    .addInsertValue("1")
                    .addInsertValue("0")
    );

    addDataTypeTest(
            new DataTypeTest("date", JsonSchemaPrimitive.STRING)
                    .addInsertValue("null")
//                    .addInsertValue("'2021-01-00'")
//                    .addInsertValue("'2021-00-00'")
//                    .addInsertValue("'0000-00-00'")
    );

    addDataTypeTest(
            new DataTypeTest("datetime", JsonSchemaPrimitive.STRING)
                    .addInsertValue("null")
//                    .addInsertValue("'0000-00-00 00:00:00'")
    );

    addDataTypeTest(
            new DataTypeTest("timestamp", JsonSchemaPrimitive.STRING)
                    .addInsertValue("null")
    );

    addDataTypeTest(
            new DataTypeTest("time", JsonSchemaPrimitive.STRING)
                    .addInsertValue("null")
//                    .addInsertValue("'-838:59:59.000000'")
    );

    addDataTypeTest(
            new DataTypeTest("varchar", JsonSchemaPrimitive.STRING)
                    .setFullSourceDataType("varchar(256) character set cp1251")
                    .addInsertValue("null")
                    .addInsertValue("'тест'")
    );

    addDataTypeTest(
            new DataTypeTest("varchar", JsonSchemaPrimitive.STRING)
                    .setFullSourceDataType("varchar(256) character set utf16")
                    .addInsertValue("null")
                    .addInsertValue("0xfffd")
    );

    addDataTypeTest(
            new DataTypeTest("varchar", JsonSchemaPrimitive.STRING)
                    .setFullSourceDataType("varchar(256)")
                    .addInsertValue("null")
                    .addInsertValue("'!\"#$%&\\'()*+,-./:;<=>?\\@[\\]^_\\`{|}~'")
    );

    addDataTypeTest(
            new DataTypeTest("varbinary", JsonSchemaPrimitive.STRING)
                    .setFullSourceDataType("varbinary(256)")
                    .addInsertValue("null")
                    .addInsertValue("'test'")
    );

    addDataTypeTest(
            new DataTypeTest("blob", JsonSchemaPrimitive.STRING)
                    .addInsertValue("null")
                    .addInsertValue("'test'")
    );

    addDataTypeTest(
            new DataTypeTest("mediumtext", JsonSchemaPrimitive.STRING)
                    .addInsertValue("null")
                    .addInsertValue("lpad('0', 16777214, '0')")
    );

    addDataTypeTest(
            new DataTypeTest("tinytext", JsonSchemaPrimitive.STRING)
                    .addInsertValue("null")
    );

    addDataTypeTest(
            new DataTypeTest("longtext", JsonSchemaPrimitive.STRING)
                    .addInsertValue("null")
    );

    addDataTypeTest(
            new DataTypeTest("text", JsonSchemaPrimitive.STRING)
                    .addInsertValue("null")
    );

    addDataTypeTest(
            new DataTypeTest("json", JsonSchemaPrimitive.STRING)
                    .addInsertValue("null")
                    .addInsertValue("'{\"a\" :10, \"b\": 15}'")
    );

    addDataTypeTest(
            new DataTypeTest("point", JsonSchemaPrimitive.OBJECT)
                    .addInsertValue("null")
                    .addInsertValue("(ST_GeomFromText('POINT(1 1)'))")
    );

    addDataTypeTest(
            new DataTypeTest("bool", JsonSchemaPrimitive.STRING)
                    .addInsertValue("null")
                    .addInsertValue("127")
                    .addInsertValue("-128")
    );

  }
}