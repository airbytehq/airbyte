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

  @Override
  protected String getImageName() {
    return "airbyte/source-mongodb-new:dev";
  }

  @Override
  protected JsonNode getConfig() throws Exception {
    return config;
  }

  @Override
  protected void setupEnvironment(TestDestinationEnv environment) throws Exception {
    mongoDBContainer = new MongoDBContainer(DockerImageName.parse("mongo:4.0.10"));
    mongoDBContainer.start();

    String connectionString = String.format("mongodb://%s:%s/?authSource=%s&tls=false",
        mongoDBContainer.getHost(),
        mongoDBContainer.getFirstMappedPort(),
        "false");

    config = Jsons.jsonNode(ImmutableMap.builder()
        .put("host", mongoDBContainer.getHost())
        .put("port", mongoDBContainer.getFirstMappedPort())
        .put("database", "test")
        .put("user", "")
        .put("password", "")
        .put("auth_source", "admin")
        .put("tls", "false")
        .put("connectionString", connectionString)
        .build());

    final MongoDatabase mongoDatabase = new MongoDatabase(connectionString, "test");

    MongoCollection<Document> collection = mongoDatabase.createCollection("acceptance_test");
    var doc1 = new Document("id", "0001")
        .append("name", "Test");
    /*var doc2 = new Document("id", "0002")
        .append("name", "Mongo");*/
    collection.insertMany(List.of(doc1));
  }

  @Override
  protected void tearDown(TestDestinationEnv testEnv) throws Exception {
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
            .withStream(CatalogHelpers.createAirbyteStream(
                    "test.acceptance_test",
                    Field.of("id", JsonSchemaPrimitive.STRING),
                    Field.of("name", JsonSchemaPrimitive.STRING))
                .withSupportedSyncModes(Lists.newArrayList(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL)))));
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
