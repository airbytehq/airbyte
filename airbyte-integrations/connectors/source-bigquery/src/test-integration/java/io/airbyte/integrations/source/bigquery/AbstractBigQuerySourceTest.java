/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.bigquery;

import static io.airbyte.integrations.source.bigquery.BigQuerySource.CONFIG_CREDS;
import static io.airbyte.integrations.source.bigquery.BigQuerySource.CONFIG_DATASET_ID;
import static io.airbyte.integrations.source.bigquery.BigQuerySource.CONFIG_PROJECT_ID;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.cloud.bigquery.Dataset;
import com.google.cloud.bigquery.DatasetInfo;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.string.Strings;
import io.airbyte.db.bigquery.BigQueryDatabase;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.sql.SQLException;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;

abstract class AbstractBigQuerySourceTest {

  private static final Path CREDENTIALS_PATH = Path.of("secrets/credentials.json");

  protected BigQueryDatabase database;
  protected Dataset dataset;
  protected JsonNode config;

  @BeforeEach
  void setUp() throws IOException, SQLException {
    if (!Files.exists(CREDENTIALS_PATH)) {
      throw new IllegalStateException(
          "Must provide path to a big query credentials file. By default {module-root}/" + CREDENTIALS_PATH
              + ". Override by setting setting path with the CREDENTIALS_PATH constant.");
    }

    final String credentialsJsonString = Files.readString(CREDENTIALS_PATH);

    final JsonNode credentialsJson = Jsons.deserialize(credentialsJsonString);
    final String projectId = credentialsJson.get(CONFIG_PROJECT_ID).asText();
    final String datasetLocation = "US";

    final String datasetId = Strings.addRandomSuffix("airbyte_tests", "_", 8);

    config = Jsons.jsonNode(ImmutableMap.builder()
        .put(CONFIG_PROJECT_ID, projectId)
        .put(CONFIG_CREDS, credentialsJsonString)
        .put(CONFIG_DATASET_ID, datasetId)
        .build());

    database = new BigQueryDatabase(config.get(CONFIG_PROJECT_ID).asText(), credentialsJsonString);

    final DatasetInfo datasetInfo =
        DatasetInfo.newBuilder(config.get(CONFIG_DATASET_ID).asText()).setLocation(datasetLocation).build();
    dataset = database.getBigQuery().create(datasetInfo);

    createTable(datasetId);
  }

  @AfterEach
  void tearDown() {
    database.cleanDataSet(dataset.getDatasetId().getDataset());
  }

  protected abstract void createTable(String datasetId) throws SQLException;

  protected abstract ConfiguredAirbyteCatalog getConfiguredCatalog();

}
