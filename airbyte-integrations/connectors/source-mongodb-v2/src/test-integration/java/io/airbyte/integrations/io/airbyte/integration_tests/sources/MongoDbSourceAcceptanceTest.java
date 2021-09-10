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
import com.mongodb.client.MongoCollection;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.db.mongodb.MongoDatabase;
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
import org.bson.Document;
import org.testcontainers.containers.MongoDBContainer;
import org.testcontainers.utility.DockerImageName;

public class MongoDbSourceAcceptanceTest extends SourceAcceptanceTest {

  private MongoDBContainer mongoDBContainer;
  private JsonNode config;
  private MongoDatabase database;

  @Override
  protected String getImageName() {
    return "airbyte/source-mongodb-v2:dev";
  }

  @Override
  protected JsonNode getConfig() throws Exception {
    return config;
  }

  @Override
  protected void setupEnvironment(TestDestinationEnv environment) throws Exception {
    mongoDBContainer = new MongoDBContainer(DockerImageName.parse("mongo:4.0.10"));
    mongoDBContainer.start();

    final JsonNode instanceConfig = Jsons.jsonNode(ImmutableMap.builder()
        .put("host", mongoDBContainer.getHost())
        .put("port", mongoDBContainer.getFirstMappedPort())
        .build());

    config = Jsons.jsonNode(ImmutableMap.builder()
        .put("instance_type", instanceConfig)
        .put("database", "test")
        .put("auth_source", "admin")
        .put("tls", false)
        .build());

    String connectionString = String.format("mongodb://%s:%s/",
        mongoDBContainer.getHost(),
        mongoDBContainer.getFirstMappedPort());

    database = new MongoDatabase(connectionString, "test");

    MongoCollection<Document> collection = database.createCollection("acceptance_test");
    var doc1 = new Document("id", "0001").append("name", "Test");
    var doc2 = new Document("id", "0002").append("name", "Mongo");
    var doc3 = new Document("id", "0003").append("name", "Source");

    collection.insertMany(List.of(doc1, doc2, doc3));
  }

  @Override
  protected void tearDown(TestDestinationEnv testEnv) throws Exception {
    database.close();
    mongoDBContainer.close();
  }

  @Override
  protected ConnectorSpecification getSpec() throws Exception {
    return Jsons.deserialize(MoreResources.readResource("spec.json"), ConnectorSpecification.class);
  }

  @Override
  protected ConfiguredAirbyteCatalog getConfiguredCatalog() throws Exception {
    return new ConfiguredAirbyteCatalog().withStreams(Lists.newArrayList(
        new ConfiguredAirbyteStream()
            .withSyncMode(SyncMode.INCREMENTAL)
            .withCursorField(Lists.newArrayList("_id"))
            .withDestinationSyncMode(DestinationSyncMode.APPEND)
            .withCursorField(List.of("_id"))
            .withStream(CatalogHelpers.createAirbyteStream(
                "test.acceptance_test",
                Field.of("_id", JsonSchemaPrimitive.STRING),
                Field.of("id", JsonSchemaPrimitive.STRING),
                Field.of("name", JsonSchemaPrimitive.STRING))
                .withSupportedSyncModes(Lists.newArrayList(SyncMode.INCREMENTAL))
                .withDefaultCursorField(List.of("_id")))));
  }

  @Override
  protected JsonNode getState() throws Exception {
    return Jsons.jsonNode(new HashMap<>());
  }

  @Override
  protected List<String> getRegexTests() throws Exception {
    return Collections.emptyList();
  }

}
