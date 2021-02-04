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
import java.util.Map.Entry;
import java.util.stream.Collectors;
import java.util.stream.Stream;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtensionContext;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.Arguments;
import org.junit.jupiter.params.provider.ArgumentsProvider;
import org.junit.jupiter.params.provider.ArgumentsSource;
import org.testcontainers.containers.GenericContainer;
import org.testcontainers.utility.DockerImageName;

public class MeiliSearchStandardTest extends TestDestination {

  private static final Integer DEFAULT_MEILI_SEARCH_PORT = 7700;
  private static final Integer EXPOSED_PORT = 7701;
  // calling localhost from within a docker container on mac.
  private static final String HOST = "http://host.docker.internal:" + EXPOSED_PORT;
  // calling localhost.
  private static final String LOCAL_HOST = "http://localhost:" + EXPOSED_PORT;
  private static final String API_KEY = "masterKey";

  private Client meiliSearchClient;
  private GenericContainer<?> genericContainer;

  @Override
  protected String getImageName() {
    return "airbyte/destination-meilisearch:dev";
  }

  @Override
  protected JsonNode getConfig() {
    final JsonNode jsonNode = Jsons.jsonNode(ImmutableMap.builder()
        .put("host", HOST)
        .put("api_key", API_KEY)
        .build());
    System.out.println("jsonNode = " + jsonNode);
    return jsonNode;
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
        .peek(r -> MoreStreams.toStream(r.fields()).map(Entry::getKey)
            .filter(fieldName -> fieldName.startsWith("_ab_pk_"))
            .findFirst().ifPresent(((ObjectNode) r)::remove))
        .collect(Collectors.toList());
  }

  @Override
  protected void setup(TestDestinationEnv testEnv) throws IOException {
    final Path meiliSearchDataDir = Files.createTempDirectory(Path.of("/tmp"), "meilisearch-integration-test");
    meiliSearchDataDir.toFile().deleteOnExit();

    genericContainer = new GenericContainer<>(DockerImageName.parse("getmeili/meilisearch:latest"))
        .withFileSystemBind(meiliSearchDataDir.toString(), "/data.ms");
    genericContainer.setPortBindings(ImmutableList.of(EXPOSED_PORT + ":" + DEFAULT_MEILI_SEARCH_PORT));
    genericContainer.start();

    final JsonNode localHostConfig = Jsons.clone(getConfig());
    ((ObjectNode) localHostConfig).put("host", LOCAL_HOST);
    meiliSearchClient = MeiliSearchDestination.getClient(localHostConfig);
  }

  @Override
  protected void tearDown(TestDestinationEnv testEnv) {
    genericContainer.stop();
  }

  protected static class MeiliSearchDataArgumentsProvider implements ArgumentsProvider {

    @Override
    public Stream<? extends Arguments> provideArguments(ExtensionContext context) {
      return Stream.of(
          Arguments.of("exchange_rate_messages_for_meilisearch.txt", "exchange_rate_catalog.json"),
          Arguments.of("edge_case_messages_for_meilisearch.txt", "edge_case_catalog_for_meilisearch.json"));
    }

  }

  // override base test in TestDestination so that use records and catalogs that work with this
  // destination. specifically that a primary key is needed.
  @Override
  @ParameterizedTest
  @ArgumentsSource(MeiliSearchDataArgumentsProvider.class)
  public void testSync(String messagesFilename, String catalogFilename) throws Exception {
    super.testSync(messagesFilename, catalogFilename);
  }

  // override base test in TestDestination so that use records and catalogs that work with this
  // destination. specifically that a primary key is needed.
  @Test
  @Override
  public void testIncrementalSync() throws Exception {
    super.testIncrementalSync("exchange_rate_messages_for_meilisearch.txt", "exchange_rate_catalog_for_meilisearch.json");
  }

}
