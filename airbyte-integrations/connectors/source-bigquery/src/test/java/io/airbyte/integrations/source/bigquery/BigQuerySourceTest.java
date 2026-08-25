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
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.cloud.bigquery.BigQuery;
import com.google.cloud.bigquery.BigQueryError;
import com.google.cloud.bigquery.BigQueryException;
import com.google.cloud.bigquery.FieldValueList;
import com.google.cloud.bigquery.Job;
import com.google.cloud.bigquery.JobInfo;
import com.google.cloud.bigquery.JobStatus;
import com.google.cloud.bigquery.QueryJobConfiguration;
import com.google.cloud.bigquery.TableResult;
import io.airbyte.commons.exceptions.ConfigErrorException;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import java.io.IOException;
import java.util.Iterator;
import org.junit.jupiter.api.Test;
import org.mockito.ArgumentCaptor;

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
  public void testQueryResultsArePaginated() throws Exception {
    final BigQuery bigQuery = mock(BigQuery.class);
    final Job job = mock(Job.class);
    final JobStatus jobStatus = mock(JobStatus.class);
    final TableResult tableResult = mock(TableResult.class);
    when(bigQuery.create(any(JobInfo.class))).thenReturn(job);
    when(job.waitFor()).thenReturn(job);
    when(job.getStatus()).thenReturn(jobStatus);
    when(jobStatus.getError()).thenReturn(null);
    when(job.getQueryResults(any())).thenReturn(tableResult);

    BigQuerySource.executeQuery(
        bigQuery,
        QueryJobConfiguration.newBuilder("SELECT 1").setUseLegacySql(false).build(),
        BigQuerySource.QUERY_RESULT_PAGE_SIZE);

    final ArgumentCaptor<BigQuery.QueryResultsOption> optionCaptor = ArgumentCaptor.forClass(BigQuery.QueryResultsOption.class);
    verify(job).getQueryResults(optionCaptor.capture());
    assertEquals(BigQuery.QueryResultsOption.pageSize(BigQuerySource.QUERY_RESULT_PAGE_SIZE), optionCaptor.getValue());
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
        "Query results for table dataset.table exceed BigQuery's maximum API response size. Select fewer columns for this stream, or use incremental sync so the table is read in smaller batches.",
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
        "Query results for table dataset.table exceed BigQuery's maximum API response size. Select fewer columns for this stream, or use incremental sync so the table is read in smaller batches.",
        configError.getMessage());
  }

  @Test
  public void testResponseTooLargeDuringResultIterationIsMappedToConfigError() {
    final BigQueryException responseTooLarge = new BigQueryException(
        403,
        "Response too large to return.",
        new BigQueryError("responseTooLarge", null, "Response too large to return."));
    final Iterator<FieldValueList> iterator = new Iterator<>() {

      private int hasNextCalls;

      @Override
      public boolean hasNext() {
        if (hasNextCalls++ == 1) {
          throw responseTooLarge;
        }
        return true;
      }

      @Override
      public FieldValueList next() {
        return mock(FieldValueList.class);
      }

    };
    final Iterator<FieldValueList> wrapped = BigQuerySource.wrapQueryResultIterator(iterator, "dataset", "table");

    assertTrue(wrapped.hasNext());
    wrapped.next();
    final ConfigErrorException configError = assertThrows(ConfigErrorException.class, wrapped::hasNext);

    assertEquals(
        "Query results for table dataset.table exceed BigQuery's maximum API response size. Select fewer columns for this stream, or use incremental sync so the table is read in smaller batches.",
        configError.getMessage());
  }

  @Test
  public void testUnrelatedQueryErrorIsNotMapped() {
    final RuntimeException exception = new IllegalArgumentException("unrelated");

    final RuntimeException mapped = BigQuerySource.mapQueryException(exception, "dataset", "table");

    assertFalse(mapped instanceof ConfigErrorException);
    assertSame(exception, mapped);
  }

  @Test
  public void testFailedQueryJobThrows() throws Exception {
    final BigQuery bigQuery = mock(BigQuery.class);
    final Job job = mock(Job.class);
    final JobStatus jobStatus = mock(JobStatus.class);
    final BigQueryError error = mock(BigQueryError.class);
    when(bigQuery.create(any(JobInfo.class))).thenReturn(job);
    when(job.waitFor()).thenReturn(job);
    when(job.getStatus()).thenReturn(jobStatus);
    when(jobStatus.getError()).thenReturn(error);

    assertThrows(
        IllegalStateException.class,
        () -> BigQuerySource.executeQuery(
            bigQuery,
            QueryJobConfiguration.newBuilder("SELECT 1").setUseLegacySql(false).build(),
            BigQuerySource.QUERY_RESULT_PAGE_SIZE));
  }

}
