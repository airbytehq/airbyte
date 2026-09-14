/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.bigquery;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertInstanceOf;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.anyString;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.cloud.bigquery.BigQueryError;
import com.google.cloud.bigquery.BigQueryException;
import com.google.cloud.bigquery.QueryParameterValue;
import io.airbyte.cdk.db.bigquery.BigQueryDatabase;
import io.airbyte.commons.exceptions.ConfigErrorException;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.commons.util.AutoCloseableIterator;
import io.airbyte.protocol.models.v0.SyncMode;
import java.io.IOException;
import java.util.Collections;
import java.util.Iterator;
import java.util.Optional;
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
  public void testResponseTooLargeIsMappedToConfigError() {
    final BigQueryException responseTooLarge = new BigQueryException(
        403,
        "Response too large to return.",
        new BigQueryError("responseTooLarge", null, "Response too large to return."));

    final RuntimeException mapped = BigQuerySource.mapQueryException(
        new RuntimeException(responseTooLarge),
        "dataset",
        "table");

    final ConfigErrorException configError = assertInstanceOf(ConfigErrorException.class, mapped);
    assertEquals(
        "Query result for table dataset.table exceeds BigQuery maximum query response size.",
        configError.getMessage());
  }

  @Test
  public void testResponseTooLargeJobFailureIsMappedToConfigError() {
    final RuntimeException mapped = BigQuerySource.mapQueryException(
        new IllegalStateException(
            "BigQuery query job failed: BigQueryError{reason=responseTooLarge, location=null, message=Response too large to return.}"),
        "dataset",
        "table");

    final ConfigErrorException configError = assertInstanceOf(ConfigErrorException.class, mapped);
    assertEquals(
        "Query result for table dataset.table exceeds BigQuery maximum query response size.",
        configError.getMessage());
  }

  @Test
  public void testResponseTooLargeDuringResultIterationIsMappedToConfigError() {
    final BigQueryException responseTooLarge = new BigQueryException(
        403,
        "Response too large to return.",
        new BigQueryError("responseTooLarge", null, "Response too large to return."));
    final Iterator<String> iterator = new Iterator<>() {

      private int hasNextCalls;

      @Override
      public boolean hasNext() {
        if (hasNextCalls++ == 1) {
          throw responseTooLarge;
        }
        return true;
      }

      @Override
      public String next() {
        return "result";
      }

    };
    final Iterator<String> wrapped = BigQuerySource.wrapQueryResultIterator(iterator, "dataset", "table");

    assertTrue(wrapped.hasNext());
    wrapped.next();
    final ConfigErrorException configError = assertThrows(ConfigErrorException.class, wrapped::hasNext);

    assertEquals(
        "Query result for table dataset.table exceeds BigQuery maximum query response size.",
        configError.getMessage());
  }

  @Test
  public void testResponseTooLargeFromQueryIsMappedToConfigError() throws Exception {
    final BigQueryDatabase database = mock(BigQueryDatabase.class);
    final BigQueryException responseTooLarge = new BigQueryException(
        403,
        "Response too large to return.",
        new BigQueryError("responseTooLarge", null, "Response too large to return."));
    when(database.query(anyString(), any(QueryParameterValue[].class))).thenThrow(responseTooLarge);

    final AutoCloseableIterator<JsonNode> iterator = new BigQuerySource().queryTableFullRefresh(
        database,
        Collections.singletonList("column"),
        "dataset",
        "table",
        SyncMode.FULL_REFRESH,
        Optional.empty());
    final ConfigErrorException configError = assertThrows(ConfigErrorException.class, iterator::hasNext);

    assertEquals(
        "Query result for table dataset.table exceeds BigQuery maximum query response size.",
        configError.getMessage());
  }

  @Test
  public void testUnrelatedQueryErrorIsNotMapped() {
    final RuntimeException exception = new IllegalArgumentException("unrelated");

    final RuntimeException mapped = BigQuerySource.mapQueryException(exception, "dataset", "table");

    assertFalse(mapped instanceof ConfigErrorException);
    assertSame(exception, mapped);
  }

}
