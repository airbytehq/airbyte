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

package io.airbyte.integrations.source.oracle;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.integrations.source.jdbc.AbstractJdbcSource;
import io.airbyte.integrations.source.jdbc.test.JdbcSourceStandardTest;
import io.airbyte.test.utils.OracleContainerHelper;
import org.apache.commons.lang3.RandomStringUtils;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.testcontainers.containers.OracleContainer;
import org.testcontainers.utility.MountableFile;

class OracleJdbcStandardSourceTest extends JdbcSourceStandardTest {

  private static OracleContainer ORACLE_DB;

  private JsonNode config;

  @BeforeAll
  static void init() {
    ORACLE_DB = new OracleContainer("epiclabs/docker-oracle-xe-11g");
    ORACLE_DB.start();
  }

  @BeforeEach
  public void setup() throws Exception {
    final String dbName = "db_" + RandomStringUtils.randomAlphabetic(10).toLowerCase();

    config = Jsons.jsonNode(ImmutableMap.builder()
        .put("host", ORACLE_DB.getHost())
        .put("port", ORACLE_DB.getFirstMappedPort())
        .put("database", dbName)
        .put("username", ORACLE_DB.getUsername())
        .put("password", ORACLE_DB.getPassword())
        .build());

    final String initScriptName = "init_" + dbName.concat(".sql");
    MoreResources.writeResource(initScriptName, "CREATE DATABASE " + dbName + ";");
    OracleContainerHelper.runSqlScript(MountableFile.forClasspathResource(initScriptName), ORACLE_DB);

    super.setup();
  }

  @Override
  public boolean supportsSchemas() {
    return true;
  }

  @Override
  public AbstractJdbcSource getSource() {
    return new OracleSource();
  }

  @Override
  public JsonNode getConfig() {
    return config;
  }

  @Override
  public String getDriverClass() {
    return OracleSource.DRIVER_CLASS;
  }

  @AfterAll
  static void cleanUp() {
    ORACLE_DB.close();
  }

}
