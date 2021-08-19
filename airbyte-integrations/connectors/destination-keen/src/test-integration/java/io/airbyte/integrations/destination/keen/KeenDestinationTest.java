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
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Comparator;
import java.util.List;
import java.util.stream.Collectors;

public class KeenDestinationTest extends DestinationAcceptanceTest {

  private static final String SECRET_FILE_PATH = "secrets/config.json";

  private final KeenHttpClient keenHttpClient = new KeenHttpClient();

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
  protected JsonNode getFailCheckConfig() throws Exception {
    ((ObjectNode) configJson).put(CONFIG_PROJECT_ID, "fake");
    ((ObjectNode) configJson).put(CONFIG_API_KEY, "fake");

    return configJson;
  }

  protected JsonNode getBaseConfigJson() {
    return Jsons.deserialize(IOs.readFile(Path.of(SECRET_FILE_PATH)));
  }

  @Override
  protected List<JsonNode> retrieveRecords(TestDestinationEnv testEnv, String streamName, String namespace, JsonNode streamSchema) throws Exception {
    String accentStrippedStreamName = KeenCharactersStripper.stripSpecialCharactersFromStreamName(streamName);

    ArrayNode array = keenHttpClient.extract(accentStrippedStreamName, projectId, apiKey);
    return Lists.newArrayList(array.elements()).stream()
        .sorted(Comparator.comparing(o -> o.get("keen").get("timestamp").textValue()))
        .map(node -> (JsonNode) ((ObjectNode) node).without("keen"))
        .collect(Collectors.toList());
  }

  @Override
  protected void setup(TestDestinationEnv testEnv) throws Exception {
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
  protected void tearDown(TestDestinationEnv testEnv) throws Exception {
    // Changes for this particular operation - get all collections - can take a couple more time to
    // propagate
    // than standard queries for the newly created collection
    Thread.sleep(5000);
    List<String> keenCollections = keenHttpClient.getAllCollectionsForProject(projectId, apiKey);

    for (String keenCollection : keenCollections) {
      keenHttpClient.eraseStream(keenCollection, projectId, apiKey);
    }
  }

  @Override
  protected void runSyncAndVerifyStateOutput(JsonNode config,
                                             List<AirbyteMessage> messages,
                                             ConfiguredAirbyteCatalog catalog,
                                             boolean runNormalization)
      throws Exception {
    super.runSyncAndVerifyStateOutput(config, messages, catalog, runNormalization);
    Thread.sleep(10000);
  }

}
