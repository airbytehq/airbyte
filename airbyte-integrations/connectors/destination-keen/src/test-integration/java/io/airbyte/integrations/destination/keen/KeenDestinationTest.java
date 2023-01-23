/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.keen;

import static io.airbyte.integrations.destination.keen.KeenDestination.CONFIG_API_KEY;
import static io.airbyte.integrations.destination.keen.KeenDestination.CONFIG_PROJECT_ID;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ArrayNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.api.client.util.Lists;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.standardtest.destination.DestinationAcceptanceTest;
import io.airbyte.integrations.standardtest.destination.comparator.AdvancedTestDataComparator;
import io.airbyte.integrations.standardtest.destination.comparator.TestDataComparator;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Comparator;
import java.util.HashSet;
import java.util.List;
import java.util.Set;
import java.util.stream.Collectors;

public class KeenDestinationTest extends DestinationAcceptanceTest {

  private static final String SECRET_FILE_PATH = "secrets/config.json";

  private final KeenHttpClient keenHttpClient = new KeenHttpClient();
  private final Set<String> collectionsToDelete = new HashSet<>();

  private String projectId;
  private String apiKey;
  private JsonNode configJson;

  @Override
  protected String getImageName() {
    return "airbyte/destination-keen:dev";
  }

  @Override
  protected JsonNode getConfig() throws Exception {
    return configJson;
  }

  @Override
  protected TestDataComparator getTestDataComparator() {
    return new AdvancedTestDataComparator();
  }

  @Override
  protected boolean supportBasicDataTypeTest() {
    return true;
  }

  @Override
  protected boolean supportArrayDataTypeTest() {
    return true;
  }

  @Override
  protected boolean supportObjectDataTypeTest() {
    return true;
  }

  @Override
  protected JsonNode getFailCheckConfig() throws Exception {
    ((ObjectNode) configJson).put(CONFIG_PROJECT_ID, "fake");
    ((ObjectNode) configJson).put(CONFIG_API_KEY, "fake");

    return configJson;
  }

  protected JsonNode getBaseConfigJson() {
    return Jsons.deserialize(IOs.readFile(Path.of(SECRET_FILE_PATH)));
  }

  @Override
  protected List<JsonNode> retrieveRecords(final TestDestinationEnv testEnv,
                                           final String streamName,
                                           final String namespace,
                                           final JsonNode streamSchema)
      throws Exception {
    final String accentStrippedStreamName = KeenCharactersStripper.stripSpecialCharactersFromStreamName(streamName);
    collectionsToDelete.add(accentStrippedStreamName);

    final ArrayNode array = keenHttpClient.extract(accentStrippedStreamName, projectId, apiKey);
    return Lists.newArrayList(array.elements()).stream()
        .sorted(Comparator.comparing(o -> o.get("keen").get("timestamp").textValue()))
        .map(node -> (JsonNode) ((ObjectNode) node).without("keen"))
        .collect(Collectors.toList());
  }

  @Override
  protected void setup(final TestDestinationEnv testEnv) throws Exception {
    if (!Files.exists(Path.of(SECRET_FILE_PATH))) {
      throw new IllegalStateException(
          "Must provide path to a file containing Keen account credentials: Project ID and Master API Key. " +
              "By default {module-root}/" + SECRET_FILE_PATH);
    }
    configJson = getBaseConfigJson();
    projectId = configJson.get(CONFIG_PROJECT_ID).asText();
    apiKey = configJson.get(CONFIG_API_KEY).asText();

  }

  @Override
  protected void tearDown(final TestDestinationEnv testEnv) throws Exception {
    for (final String keenCollection : collectionsToDelete) {
      keenHttpClient.eraseStream(keenCollection, projectId, apiKey);
    }
    collectionsToDelete.clear();
  }

  @Override
  protected void runSyncAndVerifyStateOutput(final JsonNode config,
                                             final List<AirbyteMessage> messages,
                                             final ConfiguredAirbyteCatalog catalog,
                                             final boolean runNormalization)
      throws Exception {
    super.runSyncAndVerifyStateOutput(config, messages, catalog, runNormalization);
    Thread.sleep(10000);
  }

}
