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

package io.airbyte.integrations.source.jdbc;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.db.Database;
import io.airbyte.db.Databases;
import io.airbyte.integrations.base.TestSource;
import io.airbyte.protocol.models.AirbyteCatalog;
import io.airbyte.protocol.models.CatalogHelpers;
import io.airbyte.protocol.models.ConnectorSpecification;
import io.airbyte.protocol.models.Field;
import io.airbyte.protocol.models.Field.JsonSchemaPrimitive;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.List;
import org.testcontainers.containers.PostgreSQLContainer;

public class JdbcIntegrationTest extends TestSource {

  private static final String STREAM_NAME = "id_and_name";
  private PostgreSQLContainer<?> container;
  private Database database;
  private JsonNode config;

  @Override
  protected void setup(TestDestinationEnv testEnv) throws SQLException {
    container = new PostgreSQLContainer<>("postgres:13-alpine");
    container.start();

    config = Jsons.jsonNode(ImmutableMap.builder()
        .put("username", container.getUsername())
        .put("password", container.getPassword())
        .put("jdbc_url", String.format("jdbc:postgresql://%s:%s/%s",
            container.getHost(),
            container.getFirstMappedPort(),
            container.getDatabaseName()))
        .build());

    database = Databases.createPostgresDatabase(
        config.get("username").asText(),
        config.get("password").asText(),
        config.get("jdbc_url").asText());

    database.query(ctx -> {
      ctx.fetch("CREATE TABLE id_and_name(id INTEGER, name VARCHAR(200));");
      ctx.fetch("INSERT INTO id_and_name (id, name) VALUES (1,'picard'),  (2, 'crusher'), (3, 'vash');");
      return null;
    });
  }

  @Override
  protected void tearDown(TestDestinationEnv testEnv) throws Exception {
    database.close();
    container.close();
  }

  @Override
  protected String getImageName() {
    return "airbyte/source-jdbc:dev";
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
  protected AirbyteCatalog getCatalog() {
    return CatalogHelpers.createAirbyteCatalog(
        STREAM_NAME,
        Field.of("id", JsonSchemaPrimitive.NUMBER),
        Field.of("name", JsonSchemaPrimitive.STRING));
  }

  @Override
  protected List<String> getRegexTests() throws Exception {
    return new ArrayList<>();
  }

}
