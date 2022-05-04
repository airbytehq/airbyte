/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery;

import static io.airbyte.integrations.destination.bigquery.factory.BigQueryCredentialsFactory.createCredentialsClient;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.cloud.bigquery.DatasetInfo;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.string.Strings;
import io.airbyte.integrations.destination.bigquery.factory.GoogleCredentialType;
import java.nio.file.Files;
import java.nio.file.Path;

public class BigQueryDestinationOAuthAcceptanceTest extends BigQueryDestinationAcceptanceTest {

  protected static final Path CREDENTIALS_PATH = Path.of("secrets/credentials_oauth.json");
  protected static final String CONFIG_CREDS = "credentials";

  @Override
  protected void setup(final TestDestinationEnv testEnv) throws Exception {
    if (!Files.exists(CREDENTIALS_PATH)) {
      throw new IllegalStateException(
          "Must provide path to a big query credentials file. By default {module-root}/" + CREDENTIALS_PATH
              + ". Override by setting setting path with the CREDENTIALS_PATH constant.");
    }

    final String fullConfigAsString = Files.readString(CREDENTIALS_PATH);
    final JsonNode credentialsJson = Jsons.deserialize(fullConfigAsString).get(BigQueryConsts.BIGQUERY_BASIC_CONFIG);
    final String projectId = credentialsJson.get(CONFIG_PROJECT_ID).asText();
    final String datasetLocation = "US";

    final String datasetId = Strings.addRandomSuffix("airbyte_tests", "_", 8);

    config = Jsons.jsonNode(ImmutableMap.builder()
        .put(CONFIG_PROJECT_ID, projectId)
        .put(CONFIG_CREDS, credentialsJson.get(CONFIG_CREDS))
        .put(CONFIG_DATASET_ID, datasetId)
        .put(CONFIG_DATASET_LOCATION, datasetLocation)
        .build());

    setupBigQuery(credentialsJson);
  }

  protected void setupBigQuery(final JsonNode credentialsJson) {
    bigquery = createCredentialsClient(credentialsJson, GoogleCredentialType.BIGQUERY_WITH_CREDENTIALS);
    final DatasetInfo datasetInfo =
        DatasetInfo.newBuilder(config.get(CONFIG_DATASET_ID).asText()).setLocation(config.get(CONFIG_DATASET_LOCATION).asText()).build();
    dataset = bigquery.create(datasetInfo);

    tornDown = false;
    Runtime.getRuntime()
        .addShutdownHook(
            new Thread(
                () -> {
                  if (!tornDown) {
                    tearDownBigQuery();
                  }
                }));
  }
}
