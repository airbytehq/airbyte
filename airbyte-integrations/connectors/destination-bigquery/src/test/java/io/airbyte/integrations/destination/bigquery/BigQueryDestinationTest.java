/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery;

import static org.junit.jupiter.api.Assertions.*;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import java.util.stream.Stream;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.*;

public class BigQueryDestinationTest {

  private ImmutableMap.Builder<Object, Object> configMapBuilder;

  @BeforeEach
  public void init() {
    configMapBuilder = ImmutableMap.builder()
        .put(BigQueryConsts.CONFIG_CREDS, "test_secret")
        .put(BigQueryConsts.CONFIG_DATASET_LOCATION, "US");
  }

  public static Stream<Arguments> validBigQueryIdProvider() {
    return Stream.of(
        Arguments.arguments("my-project", "my_dataset", "my_dataset"),
        Arguments.arguments("my-project", "my-project:my_dataset", "my_dataset"));
  }

  @ParameterizedTest
  @MethodSource("validBigQueryIdProvider")
  public void testGetDatasetIdSuccess(String projectId, String datasetId, String expected) throws Exception {
    JsonNode config = Jsons.jsonNode(configMapBuilder
        .put(BigQueryConsts.CONFIG_PROJECT_ID, projectId)
        .put(BigQueryConsts.CONFIG_DATASET_ID, datasetId)
        .build());

    String actual = BigQueryDestination.getDatasetId(config);

    assertEquals(expected, actual);
  }

  public static Stream<Arguments> invalidBigQueryIdProvider() {
    return Stream.of(
        Arguments.arguments("my-project", ":my_dataset", "BigQuery Dataset ID format must match '[project-id:]dataset_id': :my_dataset"),
        Arguments.arguments("my-project", "your-project:my_dataset",
            "Project ID included in Dataset ID must match Project ID field's value: Project ID is my-project, but you specified your-project in Dataset ID"));
  }

  @ParameterizedTest
  @MethodSource("invalidBigQueryIdProvider")
  public void testGetDatasetIdFail(String projectId, String datasetId, String expected) throws Exception {
    JsonNode config = Jsons.jsonNode(configMapBuilder
        .put(BigQueryConsts.CONFIG_PROJECT_ID, projectId)
        .put(BigQueryConsts.CONFIG_DATASET_ID, datasetId)
        .build());

    Exception exception = assertThrows(IllegalArgumentException.class, () -> BigQueryDestination.getDatasetId(config));

    assertEquals(expected, exception.getMessage());
  }

}
