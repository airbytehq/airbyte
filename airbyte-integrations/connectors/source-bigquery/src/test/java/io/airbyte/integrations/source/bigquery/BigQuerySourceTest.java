/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.bigquery;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import java.io.IOException;
import org.junit.jupiter.api.Test;

class BigQuerySourceTest {

  @Test
  public void testEmptyDatasetIdInConfig() throws IOException {
    JsonNode configJson = Jsons.deserialize(MoreResources.readResource("test_config_empty_datasetid.json"));
    JsonNode dbConfig = new BigQuerySource().toDatabaseConfig(configJson);
    assertTrue(dbConfig.get(BigQuerySource.CONFIG_DATASET_ID).isEmpty());
  }

  @Test
  public void testMissingDatasetIdInConfig() throws IOException {
    JsonNode configJson = Jsons.deserialize(MoreResources.readResource("test_config_missing_datasetid.json"));
    JsonNode dbConfig = new BigQuerySource().toDatabaseConfig(configJson);
    assertFalse(dbConfig.hasNonNull(BigQuerySource.CONFIG_DATASET_ID));
  }

  @Test
  public void testNullDatasetIdInConfig() throws IOException {
    JsonNode configJson = Jsons.deserialize(MoreResources.readResource("test_config_null_datasetid.json"));
    JsonNode dbConfig = new BigQuerySource().toDatabaseConfig(configJson);
    assertFalse(dbConfig.hasNonNull(BigQuerySource.CONFIG_DATASET_ID));
  }

  @Test
  public void testConfig() throws IOException {
    JsonNode configJson = Jsons.deserialize(MoreResources.readResource("test_config.json"));
    JsonNode dbConfig = new BigQuerySource().toDatabaseConfig(configJson);
    assertEquals("dataset", dbConfig.get(BigQuerySource.CONFIG_DATASET_ID).asText());
    assertEquals("project", dbConfig.get(BigQuerySource.CONFIG_PROJECT_ID).asText());
    assertEquals("credentials", dbConfig.get(BigQuerySource.CONFIG_CREDS).asText());
  }

}
