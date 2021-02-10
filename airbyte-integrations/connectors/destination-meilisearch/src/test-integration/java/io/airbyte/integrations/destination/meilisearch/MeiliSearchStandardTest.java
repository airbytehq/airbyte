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

package io.airbyte.integrations.destination.meilisearch;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.collect.ImmutableList;
import com.google.common.collect.ImmutableMap;
import com.meilisearch.sdk.Client;
import com.meilisearch.sdk.Index;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.stream.MoreStreams;
import io.airbyte.commons.text.Names;
import io.airbyte.integrations.standardtest.destination.TestDestination;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;
import java.util.stream.Collectors;
import org.testcontainers.containers.GenericContainer;
import org.testcontainers.utility.DockerImageName;

public class MeiliSearchStandardTest extends TestDestination {

  private static final Integer DEFAULT_MEILI_SEARCH_PORT = 7700;
  private static final Integer EXPOSED_PORT = 7701;

  private static final String API_KEY = "masterKey";

  private Client meiliSearchClient;
  private GenericContainer<?> genericContainer;
  private JsonNode config;

  @Override
  protected void setup(TestDestinationEnv testEnv) throws IOException {
    final Path meiliSearchDataDir = Files.createTempDirectory(Path.of("/tmp"), "meilisearch-integration-test");
    meiliSearchDataDir.toFile().deleteOnExit();

    genericContainer = new GenericContainer<>(DockerImageName.parse("getmeili/meilisearch:latest"))
        .withFileSystemBind(meiliSearchDataDir.toString(), "/data.ms");
    genericContainer.setPortBindings(ImmutableList.of(EXPOSED_PORT + ":" + DEFAULT_MEILI_SEARCH_PORT));
    genericContainer.start();

    config = Jsons.jsonNode(ImmutableMap.builder()
        .put("host", String.format("http://%s:%s", genericContainer.getHost(), EXPOSED_PORT))
        .put("api_key", API_KEY)
        .build());
    meiliSearchClient = MeiliSearchDestination.getClient(config);
  }

  @Override
  protected void tearDown(TestDestinationEnv testEnv) {
    genericContainer.stop();
  }

  @Override
  protected String getImageName() {
    return "airbyte/destination-meilisearch:dev";
  }

  @Override
  protected JsonNode getConfig() {
    return config;
  }

  @Override
  protected JsonNode getFailCheckConfig() {
    final JsonNode invalidConfig = Jsons.clone(getConfig());
    ((ObjectNode) invalidConfig).put("host", "localhost:7702");
    return invalidConfig;
  }

  @Override
  protected List<JsonNode> retrieveRecords(TestDestinationEnv env, String streamName) throws Exception {
    final Index index = meiliSearchClient.index(Names.toAlphanumericAndUnderscore(streamName));
    final String responseString = index.getDocuments();
    final JsonNode response = Jsons.deserialize(responseString);
    return MoreStreams.toStream(response.iterator())
        // strip out the airbyte primary key because the test cases only expect the data, no the airbyte
        // metadata column.
        .peek(r -> ((ObjectNode) r).remove(MeiliSearchDestination.AB_PK_COLUMN))
        .collect(Collectors.toList());
  }

}
