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
    addDataTypeTest(
            dataTypeTestBuilder("tinyint", JsonSchemaPrimitive.NUMBER)
                    .addInsertValue("null")
                    .addInsertValue("-128", "127")
                    .build()
    );

    addDataTypeTest(
            dataTypeTestBuilder("smallint", JsonSchemaPrimitive.NUMBER)
                    .addInsertValue("null")
                    .addInsertValue("-32768", "32767")
                    .build()
    );

    addDataTypeTest(
            dataTypeTestBuilder("smallint", JsonSchemaPrimitive.NUMBER)
                    .setFullSourceDataType("smallint zerofill")
                    .addInsertValue("1")
                    .build()
    );

    addDataTypeTest(
            dataTypeTestBuilder("mediumint", JsonSchemaPrimitive.NUMBER)
                    .addInsertValue("null", "-8388608", "8388607")
                    .build()
    );

    addDataTypeTest(
            dataTypeTestBuilder("mediumint", JsonSchemaPrimitive.NUMBER)
                    .setFullSourceDataType("mediumint zerofill")
                    .addInsertValue("1")
                    .build()
    );

    addDataTypeTest(
            dataTypeTestBuilder("int", JsonSchemaPrimitive.NUMBER)
                    .addInsertValue("null", "-2147483648", "2147483647")
                    .build()
    );

    addDataTypeTest(
            dataTypeTestBuilder("int", JsonSchemaPrimitive.NUMBER)
                    .setFullSourceDataType("int zerofill")
                    .addInsertValue("1")
                    .build()
    );

    addDataTypeTest(
            dataTypeTestBuilder("bigint", JsonSchemaPrimitive.NUMBER)
                    .addInsertValue("null", "9223372036854775807")
                    .build()
    );

    addDataTypeTest(
            dataTypeTestBuilder("float", JsonSchemaPrimitive.NUMBER)
                    .addInsertValue("null")
                    .build()
    );

    addDataTypeTest(
            dataTypeTestBuilder("double", JsonSchemaPrimitive.NUMBER)
                    .addInsertValue("null", "power(10, 308)", "1/power(10, 45)")
                    .build()
    );

    addDataTypeTest(
            dataTypeTestBuilder("decimal", JsonSchemaPrimitive.NUMBER)
                    .setFullSourceDataType("decimal(5,2)")
                    .addInsertValue("null")
                    .build()
    );

    addDataTypeTest(
            dataTypeTestBuilder("bit", JsonSchemaPrimitive.NUMBER)
                    .addInsertValue("null", "1", "0")
                    .build()
    );

    addDataTypeTest(
            dataTypeTestBuilder("date", JsonSchemaPrimitive.STRING)
                    .addInsertValue("null")
//                    .addInsertValue("'2021-01-00'")
//                    .addInsertValue("'2021-00-00'")
//                    .addInsertValue("'0000-00-00'")
                    .build()
    );

    addDataTypeTest(
            dataTypeTestBuilder("datetime", JsonSchemaPrimitive.STRING)
                    .addInsertValue("null")
//                    .addInsertValue("'0000-00-00 00:00:00'")
                    .build()
    );

    addDataTypeTest(
            dataTypeTestBuilder("timestamp", JsonSchemaPrimitive.STRING)
                    .addInsertValue("null")
                    .build()
    );

    addDataTypeTest(
            dataTypeTestBuilder("time", JsonSchemaPrimitive.STRING)
                    .addInsertValue("null")
//                    .addInsertValue("'-838:59:59.000000'")
                    .build()
    );

    addDataTypeTest(
            dataTypeTestBuilder("varchar", JsonSchemaPrimitive.STRING)
                    .setFullSourceDataType("varchar(256) character set cp1251")
                    .addInsertValue("null", "'тест'")
                    .build()
    );

    addDataTypeTest(
            dataTypeTestBuilder("varchar", JsonSchemaPrimitive.STRING)
                    .setFullSourceDataType("varchar(256) character set utf16")
                    .addInsertValue("null", "0xfffd")
                    .build()
    );

    addDataTypeTest(
            dataTypeTestBuilder("varchar", JsonSchemaPrimitive.STRING)
                    .setFullSourceDataType("varchar(256)")
                    .addInsertValue("null", "'!\"#$%&\\'()*+,-./:;<=>?\\@[\\]^_\\`{|}~'")
                    .build()
    );

    addDataTypeTest(
            dataTypeTestBuilder("varbinary", JsonSchemaPrimitive.STRING)
                    .setFullSourceDataType("varbinary(256)")
                    .addInsertValue("null", "'test'")
                    .build()
    );

    addDataTypeTest(
            dataTypeTestBuilder("blob", JsonSchemaPrimitive.STRING)
                    .addInsertValue("null", "'test'")
                    .build()
    );

    addDataTypeTest(
            dataTypeTestBuilder("mediumtext", JsonSchemaPrimitive.STRING)
                    .addInsertValue("null", "lpad('0', 16777214, '0')")
                    .build()
    );

    addDataTypeTest(
            dataTypeTestBuilder("tinytext", JsonSchemaPrimitive.STRING)
                    .addInsertValue("null")
                    .build()
    );

    addDataTypeTest(
            dataTypeTestBuilder("longtext", JsonSchemaPrimitive.STRING)
                    .addInsertValue("null")
                    .build()
    );

    addDataTypeTest(
            dataTypeTestBuilder("text", JsonSchemaPrimitive.STRING)
                    .addInsertValue("null")
                    .build()
    );

    addDataTypeTest(
            dataTypeTestBuilder("json", JsonSchemaPrimitive.STRING)
                    .addInsertValue("null", "'{\"a\" :10, \"b\": 15}'")
                    .build()
    );

    addDataTypeTest(
            dataTypeTestBuilder("point", JsonSchemaPrimitive.OBJECT)
                    .addInsertValue("null", "(ST_GeomFromText('POINT(1 1)'))")
                    .build()
    );

    addDataTypeTest(
            dataTypeTestBuilder("bool", JsonSchemaPrimitive.STRING)
                    .addInsertValue("null", "127", "-128")
                    .build()
    );

  }
}