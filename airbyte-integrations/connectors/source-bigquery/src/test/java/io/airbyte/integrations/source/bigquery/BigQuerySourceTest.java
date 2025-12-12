/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.bigquery;

import static org.junit.jupiter.api.Assertions.*;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import java.io.IOException;
import org.junit.jupiter.api.Test;

class BigQuerySourceTest {

  @Test
  public void testEmptyDatasetIdInConfig() throws IOException {
    final JsonNode configJson = Jsons.deserialize(MoreResources.readResource("test_config_empty_datasetid.json"));
    final JsonNode dbConfig = new BigQuerySource().toDatabaseConfig(configJson);
    assertTrue(dbConfig.get(BigQuerySource.CONFIG_DATASET_ID).isEmpty());
  }

  @Test
  public void testMissingDatasetIdInConfig() throws IOException {
    final JsonNode configJson = Jsons.deserialize(MoreResources.readResource("test_config_missing_datasetid.json"));
    final JsonNode dbConfig = new BigQuerySource().toDatabaseConfig(configJson);
    assertFalse(dbConfig.hasNonNull(BigQuerySource.CONFIG_DATASET_ID));
  }

  @Test
  public void testNullDatasetIdInConfig() throws IOException {
    final JsonNode configJson = Jsons.deserialize(MoreResources.readResource("test_config_null_datasetid.json"));
    final JsonNode dbConfig = new BigQuerySource().toDatabaseConfig(configJson);
    assertFalse(dbConfig.hasNonNull(BigQuerySource.CONFIG_DATASET_ID));
  }

  @Test
  public void testConfig() throws IOException {
    final JsonNode configJson = Jsons.deserialize(MoreResources.readResource("test_config.json"));
    final JsonNode dbConfig = new BigQuerySource().toDatabaseConfig(configJson);
    assertEquals("dataset", dbConfig.get(BigQuerySource.CONFIG_DATASET_ID).asText());
    assertEquals("project", dbConfig.get(BigQuerySource.CONFIG_PROJECT_ID).asText());
    assertEquals("credentials", dbConfig.get(BigQuerySource.CONFIG_CREDS).asText());
  }

  @Test
  public void testMultiProjectConfig() throws IOException {
    // Create a test config JSON with project_ids array
    final String configJsonSource = """
                                    {
                                      "project_id": "",
                                      "project_ids": ["project-1", "project-2", "project-3"],
                                      "credentials_json": "credentials"
                                    }
                                    """;

    final JsonNode configJson = Jsons.deserialize(configJsonSource);
    final JsonNode dbConfig = new BigQuerySource().toDatabaseConfig(configJson);

    assertEquals("project-1", dbConfig.get(BigQuerySource.CONFIG_PROJECT_ID).asText());
    assertEquals("credentials", dbConfig.get(BigQuerySource.CONFIG_CREDS).asText());
    assertTrue(dbConfig.has(BigQuerySource.CONFIG_PROJECT_IDS));
    assertEquals(3, dbConfig.get(BigQuerySource.CONFIG_PROJECT_IDS).size());
    assertEquals("project-1", dbConfig.get(BigQuerySource.CONFIG_PROJECT_IDS).get(0).asText());
  }

  @Test
  public void testMultipleProjectsMultipleDatasetIds() throws IOException {
    final String configJsonSource = """
                                    {
                                      "project_ids": ["project-1", "project-2", "project-3"],
                                      "dataset_ids": ["dataset-1", "dataset-2"],
                                      "credentials_json": "credentials"
                                    }
                                    """;

    final JsonNode configJson = Jsons.deserialize(configJsonSource);
    final JsonNode dbConfig = new BigQuerySource().toDatabaseConfig(configJson);

    // First project used for billing
    assertEquals("project-1", dbConfig.get(BigQuerySource.CONFIG_PROJECT_ID).asText());
    assertEquals("credentials", dbConfig.get(BigQuerySource.CONFIG_CREDS).asText());

    // project_ids preserved
    assertTrue(dbConfig.has(BigQuerySource.CONFIG_PROJECT_IDS));
    assertEquals(3, dbConfig.get(BigQuerySource.CONFIG_PROJECT_IDS).size());

    // dataset_ids preserved
    assertTrue(dbConfig.has(BigQuerySource.CONFIG_DATASET_IDS));
    assertEquals(2, dbConfig.get(BigQuerySource.CONFIG_DATASET_IDS).size());
    assertEquals("dataset-1", dbConfig.get(BigQuerySource.CONFIG_DATASET_IDS).get(0).asText());
  }

  @Test
  public void testMissingBothProjectIdAndProjectIds() {
    final String configJsonSource = """
                                    {
                                      "credentials_json": "credentials"
                                    }
                                    """;

    final JsonNode configJson = Jsons.deserialize(configJsonSource);

    assertThrows(IllegalArgumentException.class, () -> {
      new BigQuerySource().toDatabaseConfig(configJson);
    });
  }

  @Test
  public void testEmptyProjectIdWithEmptyProjectIds() {
    final String configJsonSource = """
                                    {
                                      "project_id": "",
                                      "project_ids": [],
                                      "credentials_json": "credentials"
                                    }
                                    """;

    final JsonNode configJson = Jsons.deserialize(configJsonSource);

    assertThrows(IllegalArgumentException.class, () -> {
      new BigQuerySource().toDatabaseConfig(configJson);
    });
  }

  @Test
  public void testSingleProjectModeIgnoresDatasetIds() throws IOException {
    // When using single project mode (project_id), dataset_ids should be ignored
    final String configJsonSource = """
                                    {
                                      "project_id": "my-project",
                                      "dataset_id": "my-dataset",
                                      "dataset_ids": ["dataset-1", "dataset-2"],
                                      "credentials_json": "credentials"
                                    }
                                    """;

    final JsonNode configJson = Jsons.deserialize(configJsonSource);
    final JsonNode dbConfig = new BigQuerySource().toDatabaseConfig(configJson);

    assertEquals("my-project", dbConfig.get(BigQuerySource.CONFIG_PROJECT_ID).asText());
    assertEquals("my-dataset", dbConfig.get(BigQuerySource.CONFIG_DATASET_ID).asText());
    // In single-project mode, dataset_ids should NOT be in the config
    assertFalse(dbConfig.has(BigQuerySource.CONFIG_DATASET_IDS));
    assertFalse(dbConfig.has(BigQuerySource.CONFIG_PROJECT_IDS));
  }

  @Test
  public void testMultiProjectModeIgnoresDatasetId() throws IOException {
    // When using multi-project mode (project_ids), dataset_id should be ignored
    final String configJsonSource = """
                                    {
                                      "project_ids": ["project-1", "project-2"],
                                      "dataset_id": "ignored-dataset",
                                      "dataset_ids": ["dataset-1", "dataset-2"],
                                      "credentials_json": "credentials"
                                    }
                                    """;

    final JsonNode configJson = Jsons.deserialize(configJsonSource);
    final JsonNode dbConfig = new BigQuerySource().toDatabaseConfig(configJson);

    assertEquals("project-1", dbConfig.get(BigQuerySource.CONFIG_PROJECT_ID).asText());
    assertTrue(dbConfig.has(BigQuerySource.CONFIG_PROJECT_IDS));
    assertTrue(dbConfig.has(BigQuerySource.CONFIG_DATASET_IDS));
    // In multi-project mode, dataset_id should NOT be in the config
    assertFalse(dbConfig.has(BigQuerySource.CONFIG_DATASET_ID));
  }

}
