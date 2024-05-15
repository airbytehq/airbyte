/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery.uploader;

import static io.airbyte.integrations.destination.bigquery.formatter.BigQueryRecordFormatter.*;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.cloud.bigquery.BigQuery;
import com.google.cloud.bigquery.BigQueryException;
import com.google.cloud.bigquery.FormatOptions;
import com.google.cloud.bigquery.JobId;
import com.google.cloud.bigquery.JobInfo;
import com.google.cloud.bigquery.TableDataWriteChannel;
import com.google.cloud.bigquery.TableId;
import com.google.cloud.bigquery.WriteChannelConfiguration;
import io.airbyte.commons.exceptions.ConfigErrorException;
import io.airbyte.integrations.destination.bigquery.BigQueryUtils;
import io.airbyte.integrations.destination.bigquery.formatter.BigQueryRecordFormatter;
import io.airbyte.integrations.destination.bigquery.uploader.config.UploaderConfig;
import io.airbyte.integrations.destination.bigquery.writer.BigQueryTableWriter;
import java.io.IOException;
import java.util.HashSet;
import java.util.Set;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class BigQueryUploaderFactory {

  private static final Logger LOGGER = LoggerFactory.getLogger(BigQueryUploaderFactory.class);

  private static final int HTTP_STATUS_CODE_FORBIDDEN = 403;
  private static final int HTTP_STATUS_CODE_NOT_FOUND = 404;

  private static final String CONFIG_ERROR_MSG = """
                                                    Failed to write to destination schema.

                                                   1. Make sure you have all required permissions for writing to the schema.

                                                   2. Make sure that the actual destination schema's location corresponds to location provided
                                                     in connector's config.

                                                   3. Try to change the "Destination schema" from "Mirror Source Structure" (if it's set) tp the
                                                   "Destination Default" option.

                                                 More details:
                                                 """;

  public static BigQueryDirectUploader getUploader(final UploaderConfig uploaderConfig)
      throws IOException {
    final String dataset = uploaderConfig.getParsedStream().getId().getRawNamespace();
    final String datasetLocation = BigQueryUtils.getDatasetLocation(uploaderConfig.getConfig());
    final Set<String> existingDatasets = new HashSet<>();

    final BigQueryRecordFormatter recordFormatter = uploaderConfig.getFormatter();

    final TableId targetTable = TableId.of(dataset, uploaderConfig.getTargetTableName());

    BigQueryUtils.createSchemaAndTableIfNeeded(
        uploaderConfig.getBigQuery(),
        existingDatasets,
        dataset,
        datasetLocation);

    return getBigQueryDirectUploader(
        uploaderConfig.getConfig(),
        targetTable,
        uploaderConfig.getBigQuery(),
        datasetLocation,
        recordFormatter);
  }

  private static BigQueryDirectUploader getBigQueryDirectUploader(
                                                                  final JsonNode config,
                                                                  final TableId targetTable,
                                                                  final BigQuery bigQuery,
                                                                  final String datasetLocation,
                                                                  final BigQueryRecordFormatter formatter) {
    // https://cloud.google.com/bigquery/docs/loading-data-local#loading_data_from_a_local_data_source
    LOGGER.info("Will write raw data to {} with schema {}", targetTable, SCHEMA_V2);
    final WriteChannelConfiguration writeChannelConfiguration =
        WriteChannelConfiguration.newBuilder(targetTable)
            .setCreateDisposition(JobInfo.CreateDisposition.CREATE_IF_NEEDED)
            .setSchema(SCHEMA_V2)
            .setFormatOptions(FormatOptions.json())
            .build(); // new-line delimited json.

    final JobId job = JobId.newBuilder()
        .setRandomJob()
        .setLocation(datasetLocation)
        .setProject(bigQuery.getOptions().getProjectId())
        .build();

    final TableDataWriteChannel writer;

    try {
      writer = bigQuery.writer(job, writeChannelConfiguration);
    } catch (final BigQueryException e) {
      if (e.getCode() == HTTP_STATUS_CODE_FORBIDDEN || e.getCode() == HTTP_STATUS_CODE_NOT_FOUND) {
        throw new ConfigErrorException(CONFIG_ERROR_MSG + e);
      } else {
        throw new BigQueryException(e.getCode(), e.getMessage());
      }
    }

    // this this optional value. If not set - use default client's value (15MiG)
    final Integer bigQueryClientChunkSizeFomConfig =
        BigQueryUtils.getBigQueryClientChunkSize(config);
    if (bigQueryClientChunkSizeFomConfig != null) {
      writer.setChunkSize(bigQueryClientChunkSizeFomConfig);
    }

    return new BigQueryDirectUploader(
        targetTable,
        new BigQueryTableWriter(writer),
        bigQuery,
        formatter);
  }

}
