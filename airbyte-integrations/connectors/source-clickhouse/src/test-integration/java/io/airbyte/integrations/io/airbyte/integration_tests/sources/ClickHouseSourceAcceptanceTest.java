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
import com.google.common.collect.Lists;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.db.Databases;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.source.clickhouse.ClickHouseSource;
import io.airbyte.integrations.source.jdbc.SourceJdbcUtils;
import io.airbyte.integrations.standardtest.source.SourceAcceptanceTest;
import io.airbyte.integrations.standardtest.source.TestDestinationEnv;
import io.airbyte.protocol.models.CatalogHelpers;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.ConnectorSpecification;
import io.airbyte.protocol.models.DestinationSyncMode;
import io.airbyte.protocol.models.Field;
import io.airbyte.protocol.models.JsonSchemaPrimitive;
import io.airbyte.protocol.models.SyncMode;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import org.testcontainers.containers.ClickHouseContainer;

public class ClickHouseSourceAcceptanceTest extends SourceAcceptanceTest {

  private ClickHouseContainer db;
  private JsonNode config;
  private static final String STREAM_NAME = "id_and_name";
  private static final String STREAM_NAME2 = "starships";
  private static final String SCHEMA_NAME = "default";

  @Override
  protected String getImageName() {
    return "airbyte/source-clickhouse:dev";
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
    return new ConfiguredAirbyteCatalog().withStreams(Lists.newArrayList(
        new ConfiguredAirbyteStream()
            .withSyncMode(SyncMode.INCREMENTAL)
            .withCursorField(Lists.newArrayList("id"))
            .withDestinationSyncMode(DestinationSyncMode.APPEND)
            .withStream(CatalogHelpers.createAirbyteStream(
                String.format("%s.%s", config.get("database").asText(), STREAM_NAME),
                Field.of("id", JsonSchemaPrimitive.NUMBER),
                Field.of("name", JsonSchemaPrimitive.STRING))
                .withSupportedSyncModes(Lists.newArrayList(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL))),
        new ConfiguredAirbyteStream()
            .withSyncMode(SyncMode.INCREMENTAL)
            .withCursorField(Lists.newArrayList("id"))
            .withDestinationSyncMode(DestinationSyncMode.APPEND)
            .withStream(CatalogHelpers.createAirbyteStream(
                String.format("%s.%s", config.get("database").asText(), STREAM_NAME2),
                Field.of("id", JsonSchemaPrimitive.NUMBER),
                Field.of("name", JsonSchemaPrimitive.STRING))
                .withSupportedSyncModes(Lists.newArrayList(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL)))));
  }

  @Override
  protected JsonNode getState() {
    return Jsons.jsonNode(new HashMap<>());
  }

  @Override
  protected List<String> getRegexTests() {
    return Collections.emptyList();
  }

  @Override
  protected void setupEnvironment(TestDestinationEnv environment) throws Exception {
    db = new ClickHouseContainer("yandex/clickhouse-server:21.3.10.1-alpine");
    db.start();

    config = Jsons.jsonNode(ImmutableMap.builder()
        .put("host", db.getHost())
        .put("port", db.getFirstMappedPort())
        .put("database", SCHEMA_NAME)
        .put("username", db.getUsername())
        .put("password", db.getPassword())
        .build());

    JdbcDatabase database = Databases.createJdbcDatabase(
        config.get("username").asText(),
        config.get("password").asText(),
        String.format("jdbc:clickhouse://%s:%s/%s",
            config.get("host").asText(),
            config.get("port").asText(),
            config.get("database").asText()),
        ClickHouseSource.DRIVER_CLASS);

    final String table1 = SourceJdbcUtils.getFullyQualifiedTableName(SCHEMA_NAME, STREAM_NAME);
    final String createTable1 =
        String.format("CREATE TABLE IF NOT EXISTS %s (id INTEGER, name VARCHAR(200)) ENGINE = TinyLog \n", table1);
    final String table2 = SourceJdbcUtils.getFullyQualifiedTableName(SCHEMA_NAME, STREAM_NAME2);
    final String createTable2 =
        String.format("CREATE TABLE IF NOT EXISTS %s (id INTEGER, name VARCHAR(200)) ENGINE = TinyLog \n", table2);
    database.execute(connection -> {
      connection.createStatement().execute(createTable1);
      connection.createStatement().execute(createTable2);
    });

    String insertTestData = String.format("INSERT INTO %s (id, name) VALUES (1,'picard'),  (2, 'crusher'), (3, 'vash');\n", table1);
    String insertTestData2 = String.format("INSERT INTO %s (id, name) VALUES (1,'enterprise-d'),  (2, 'defiant'), (3, 'yamato');\n", table2);
    database.execute(connection -> {
      connection.createStatement().execute(insertTestData);
      connection.createStatement().execute(insertTestData2);
    });

    database.close();
  }

  @Override
  protected void tearDown(TestDestinationEnv testEnv) {
    db.close();
    db.stop();

  }

}
