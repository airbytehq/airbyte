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
  protected Database setupDatabase(JsonNode config) {
    return Databases.createDatabase(
            config.get("username").asText(),
            config.get("password").asText(),
            String.format("jdbc:mysql://%s:%s/%s",
                    config.get("host").asText(),
                    config.get("port").asText(),
                    config.get("database").asText()),
            "com.mysql.cj.jdbc.Driver",
            SQLDialect.MYSQL);
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
                    .setCreateTablePatternSQL("CREATE TABLE %1$s(test_column %2$s zerofill);")
                    .addInsertValue("1")
    );
  }
}
