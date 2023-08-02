/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import java.util.Collections;
import java.util.Map;
import java.util.stream.Stream;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.Arguments;
import org.junit.jupiter.params.provider.MethodSource;

public class BigQueryUtilsTest {

  private ImmutableMap.Builder<Object, Object> configMapBuilder;

  @BeforeEach
  public void init() {
    configMapBuilder = ImmutableMap.builder()
        .put(BigQueryConsts.CONFIG_CREDS, "test_secret")
        .put(BigQueryConsts.CONFIG_DATASET_LOCATION, "US");
  }

  @ParameterizedTest
  @MethodSource("validBigQueryIdProvider")
  public void testGetDatasetIdSuccess(final String projectId, final String datasetId, final String expected) {
    final JsonNode config = Jsons.jsonNode(configMapBuilder
        .put(BigQueryConsts.CONFIG_PROJECT_ID, projectId)
        .put(BigQueryConsts.CONFIG_DATASET_ID, datasetId)
        .build());

    final String actual = BigQueryUtils.getDatasetId(config);

    assertEquals(expected, actual);
  }

  @ParameterizedTest
  @MethodSource("invalidBigQueryIdProvider")
  public void testGetDatasetIdFail(final String projectId, final String datasetId, final String expected) {
    final JsonNode config = Jsons.jsonNode(configMapBuilder
        .put(BigQueryConsts.CONFIG_PROJECT_ID, projectId)
        .put(BigQueryConsts.CONFIG_DATASET_ID, datasetId)
        .build());

    final Exception exception = assertThrows(IllegalArgumentException.class, () -> BigQueryUtils.getDatasetId(config));

    assertEquals(expected, exception.getMessage());
  }

  @Test
  public void testIsUsingJsonCredentials() {
    // empty
    final JsonNode emptyConfig = Jsons.jsonNode(Collections.emptyMap());
    assertFalse(BigQueryUtils.isUsingJsonCredentials(emptyConfig));

    // empty text
    final JsonNode emptyTextConfig = Jsons.jsonNode(Map.of(BigQueryConsts.CONFIG_CREDS, ""));
    assertFalse(BigQueryUtils.isUsingJsonCredentials(emptyTextConfig));

    // non-empty text
    final JsonNode nonEmptyTextConfig = Jsons.jsonNode(
        Map.of(BigQueryConsts.CONFIG_CREDS, "{ \"service_account\": \"test@airbyte.io\" }"));
    assertTrue(BigQueryUtils.isUsingJsonCredentials(nonEmptyTextConfig));

    // object
    final JsonNode objectConfig = Jsons.jsonNode(Map.of(
        BigQueryConsts.CONFIG_CREDS, Jsons.jsonNode(Map.of("service_account", "test@airbyte.io"))));
    assertTrue(BigQueryUtils.isUsingJsonCredentials(objectConfig));
  }

  private static Stream<Arguments> validBigQueryIdProvider() {
    return Stream.of(
        Arguments.arguments("my-project", "my_dataset", "my_dataset"),
        Arguments.arguments("my-project", "my-project:my_dataset", "my_dataset"));
  }

  private static Stream<Arguments> invalidBigQueryIdProvider() {
    return Stream.of(
        Arguments.arguments("my-project", ":my_dataset",
            "Project ID included in Dataset ID must match Project ID field's value: Project ID is `my-project`, but you specified `` in Dataset ID"),
        Arguments.arguments("my-project", "your-project:my_dataset",
            "Project ID included in Dataset ID must match Project ID field's value: Project ID is `my-project`, but you specified `your-project` in Dataset ID"));
  }

}
