/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
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
import io.airbyte.integrations.standardtest.destination.DestinationAcceptanceTest;
import io.airbyte.integrations.standardtest.destination.comparator.AdvancedTestDataComparator;
import io.airbyte.integrations.standardtest.destination.comparator.TestDataComparator;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Comparator;
import java.util.List;
import java.util.stream.Collectors;
import org.testcontainers.containers.GenericContainer;
import org.testcontainers.utility.DockerImageName;

public class MeiliSearchDestinationAcceptanceTest extends DestinationAcceptanceTest {

  private static final Integer DEFAULT_MEILI_SEARCH_PORT = 7700;
  private static final Integer EXPOSED_PORT = 7701;

  private static final String API_KEY = "masterKey";

  private Client meiliSearchClient;
  private GenericContainer<?> genericContainer;
  private JsonNode config;

  @Override
  protected void setup(final TestDestinationEnv testEnv) throws IOException {
    final Path meiliSearchDataDir = Files.createTempDirectory(Path.of("/tmp"), "meilisearch-integration-test");
    meiliSearchDataDir.toFile().deleteOnExit();

    genericContainer = new GenericContainer<>(DockerImageName.parse("getmeili/meilisearch:v0.24.0"))
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
  protected void tearDown(final TestDestinationEnv testEnv) {
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
  protected List<JsonNode> retrieveRecords(final TestDestinationEnv env,
                                           final String streamName,
                                           final String namespace,
                                           final JsonNode streamSchema)
      throws Exception {
    final Index index = meiliSearchClient.index(Names.toAlphanumericAndUnderscore(streamName));
    final String responseString = index.getDocuments();
    final JsonNode response = Jsons.deserialize(responseString);
    return MoreStreams.toStream(response.iterator())
        // strip out the airbyte primary key because the test cases only expect the data, no the airbyte
        // metadata column.
        // We also sort the data by "emitted_at" and then remove that column, because the test cases only
        // expect data,
        // not the airbyte metadata column.
        .peek(r -> ((ObjectNode) r).remove(MeiliSearchDestination.AB_PK_COLUMN))
        .sorted(Comparator.comparing(o -> o.get(MeiliSearchDestination.AB_EMITTED_AT_COLUMN).asText()))
        .peek(r -> ((ObjectNode) r).remove(MeiliSearchDestination.AB_EMITTED_AT_COLUMN))
        .collect(Collectors.toList());
  }

}
