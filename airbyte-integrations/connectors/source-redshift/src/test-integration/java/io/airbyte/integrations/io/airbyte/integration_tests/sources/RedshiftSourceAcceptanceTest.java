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
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.db.Databases;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.db.jdbc.JdbcUtils;
import io.airbyte.integrations.source.redshift.RedshiftSource;
import io.airbyte.integrations.standardtest.source.SourceAcceptanceTest;
import io.airbyte.integrations.standardtest.source.TestDestinationEnv;
import io.airbyte.protocol.models.CatalogHelpers;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.ConnectorSpecification;
import io.airbyte.protocol.models.Field;
import io.airbyte.protocol.models.JsonSchemaPrimitive;
import java.nio.file.Path;
import java.sql.SQLException;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import org.apache.commons.lang3.RandomStringUtils;

public class RedshiftSourceAcceptanceTest extends SourceAcceptanceTest {

  // This test case expects an active redshift cluster that is useable from outside of vpc
  private JsonNode config;
  private JdbcDatabase database;
  private String schemaName;
  private String streamName;

  private static JsonNode getStaticConfig() {
    return Jsons.deserialize(IOs.readFile(Path.of("secrets/config.json")));
  }

  @Override
  protected void setupEnvironment(TestDestinationEnv environment) throws Exception {
    config = getStaticConfig();

    database = Databases.createJdbcDatabase(
        config.get("username").asText(),
        config.get("password").asText(),
        String.format("jdbc:redshift://%s:%s/%s",
            config.get("host").asText(),
            config.get("port").asText(),
            config.get("database").asText()),
        RedshiftSource.DRIVER_CLASS);

    schemaName = ("integration_test_" + RandomStringUtils.randomAlphanumeric(5)).toLowerCase();
    final String createSchemaQuery = String.format("CREATE SCHEMA %s", schemaName);
    database.execute(connection -> {
      connection.createStatement().execute(createSchemaQuery);
    });

    streamName = "customer";
    final String fqTableName = JdbcUtils.getFullyQualifiedTableName(schemaName, streamName);
    String createTestTable =
        String.format("CREATE TABLE IF NOT EXISTS %s (c_custkey INTEGER, c_name VARCHAR(16), c_nation VARCHAR(16));\n", fqTableName);
    database.execute(connection -> {
      connection.createStatement().execute(createTestTable);
    });

    String insertTestData = String.format("insert into %s values (1, 'Chris', 'France');\n", fqTableName);
    database.execute(connection -> {
      connection.createStatement().execute(insertTestData);
    });
  }

  @Override
  protected void tearDown(TestDestinationEnv testEnv) throws SQLException {
    final String dropSchemaQuery = String.format("DROP SCHEMA IF EXISTS %s CASCADE", schemaName);
    database.execute(connection -> connection.createStatement().execute(dropSchemaQuery));
  }

  @Override
  protected String getImageName() {
    return "airbyte/source-redshift:dev";
  }

  @Override
  protected ConnectorSpecification getSpec() throws Exception {
    return Jsons.deserialize(MoreResources.readResource("spec.json"), ConnectorSpecification.class);
  }

  @Override
  protected JsonNode getConfig() {
    return config;
  }

  @Override
  protected ConfiguredAirbyteCatalog getConfiguredCatalog() {
    return CatalogHelpers.createConfiguredAirbyteCatalog(
        streamName,
        schemaName,
        Field.of("c_custkey", JsonSchemaPrimitive.NUMBER),
        Field.of("c_name", JsonSchemaPrimitive.STRING),
        Field.of("c_nation", JsonSchemaPrimitive.STRING));
  }

  @Override
  protected List<String> getRegexTests() {
    return Collections.emptyList();
  }

  @Override
  protected JsonNode getState() {
    return Jsons.jsonNode(new HashMap<>());
  }

}
