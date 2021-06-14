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

package io.airbyte.integrations.source.postgres;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.string.Strings;
import io.airbyte.db.jdbc.PostgresJdbcStreamingQueryConfiguration;
import io.airbyte.integrations.base.IntegrationRunner;
import io.airbyte.integrations.base.Source;
import io.airbyte.integrations.source.jdbc.AbstractJdbcSource;
import io.airbyte.integrations.source.jdbc.test.JdbcStressTest;
import io.airbyte.test.utils.PostgreSQLContainerHelper;
import java.util.Optional;
import java.util.Set;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Disabled;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.testcontainers.containers.PostgreSQLContainer;
import org.testcontainers.utility.MountableFile;

/**
 * Runs the stress tests in the source-jdbc test module. We want this module to run these tests
 * itself as a sanity check. The trade off here is that this class is duplicated from the one used
 * in source-postgres.
 */
@Disabled
class PostgresStressTest extends JdbcStressTest {

  private static PostgreSQLContainer<?> PSQL_DB;

  private JsonNode config;

  @BeforeAll
  static void init() {
    PSQL_DB = new PostgreSQLContainer<>("postgres:13-alpine");
    PSQL_DB.start();
  }

  @BeforeEach
  public void setup() throws Exception {
    final String dbName = Strings.addRandomSuffix("db", "_", 10).toLowerCase();

    config = Jsons.jsonNode(ImmutableMap.builder()
        .put("host", PSQL_DB.getHost())
        .put("port", PSQL_DB.getFirstMappedPort())
        .put("database", dbName)
        .put("username", PSQL_DB.getUsername())
        .put("password", PSQL_DB.getPassword())
        .put("ssl", false)
        .build());

    final String initScriptName = "init_" + dbName.concat(".sql");
    final String tmpFilePath = IOs.writeFileToRandomTmpDir(initScriptName, "CREATE DATABASE " + dbName + ";");
    PostgreSQLContainerHelper.runSqlScript(MountableFile.forHostPath(tmpFilePath), PSQL_DB);

    super.setup();
  }

  @Override
  public Optional<String> getDefaultSchemaName() {
    return Optional.of("public");
  }

  @Override
  public AbstractJdbcSource getSource() {
    return new PostgresTestSource();
  }

  @Override
  public JsonNode getConfig() {
    return config;
  }

  @Override
  public String getDriverClass() {
    return PostgresTestSource.DRIVER_CLASS;
  }

  @AfterAll
  static void cleanUp() {
    PSQL_DB.close();
  }

  private static class PostgresTestSource extends AbstractJdbcSource implements Source {

    private static final Logger LOGGER = LoggerFactory.getLogger(PostgresTestSource.class);

    static final String DRIVER_CLASS = "org.postgresql.Driver";

    public PostgresTestSource() {
      super(DRIVER_CLASS, new PostgresJdbcStreamingQueryConfiguration());
    }

    @Override
    public JsonNode toJdbcConfig(JsonNode config) {
      ImmutableMap.Builder<Object, Object> configBuilder = ImmutableMap.builder()
          .put("username", config.get("username").asText())
          .put("jdbc_url", String.format("jdbc:postgresql://%s:%s/%s",
              config.get("host").asText(),
              config.get("port").asText(),
              config.get("database").asText()));

      if (config.has("password")) {
        configBuilder.put("password", config.get("password").asText());
      }

      return Jsons.jsonNode(configBuilder.build());
    }

    @Override
    public Set<String> getExcludedInternalNameSpaces() {
      return Set.of("information_schema", "pg_catalog", "pg_internal", "catalog_history");
    }

    public static void main(String[] args) throws Exception {
      final Source source = new PostgresTestSource();
      LOGGER.info("starting source: {}", PostgresTestSource.class);
      new IntegrationRunner(source).run(args);
      LOGGER.info("completed source: {}", PostgresTestSource.class);
    }

  }

}
