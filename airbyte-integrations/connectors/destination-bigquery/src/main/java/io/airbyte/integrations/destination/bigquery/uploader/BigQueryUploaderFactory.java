/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery.uploader;

import static software.amazon.awssdk.http.HttpStatusCode.FORBIDDEN;
import static software.amazon.awssdk.http.HttpStatusCode.NOT_FOUND;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.cloud.bigquery.BigQuery;
import com.google.cloud.bigquery.BigQueryException;
import com.google.cloud.bigquery.FormatOptions;
import com.google.cloud.bigquery.JobId;
import com.google.cloud.bigquery.JobInfo;
import com.google.cloud.bigquery.Schema;
import com.google.cloud.bigquery.TableDataWriteChannel;
import com.google.cloud.bigquery.TableId;
import com.google.cloud.bigquery.WriteChannelConfiguration;
import io.airbyte.commons.exceptions.ConfigErrorException;
import io.airbyte.integrations.base.TypingAndDedupingFlag;
import io.airbyte.integrations.destination.bigquery.BigQueryUtils;
import io.airbyte.integrations.destination.bigquery.formatter.BigQueryRecordFormatter;
import io.airbyte.integrations.destination.bigquery.uploader.config.UploaderConfig;
import io.airbyte.integrations.destination.bigquery.writer.BigQueryTableWriter;
import java.io.IOException;
import java.util.HashSet;
import java.util.Set;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ConcurrentMap;

import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair;
import org.checkerframework.checker.units.qual.N;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class BigQueryUploaderFactory {

  private static final Logger LOGGER = LoggerFactory.getLogger(BigQueryUploaderFactory.class);
  private static final ConcurrentMap<AirbyteStreamNameNamespacePair, String> airbyteStreamNameNamespacePairToJob = new ConcurrentHashMap<>();

  private static final String CONFIG_ERROR_MSG = """
                                                    Failed to write to destination schema.

                                                   1. Make sure you have all required permissions for writing to the schema.

                                                   2. Make sure that the actual destination schema's location corresponds to location provided
                                                     in connector's config.

                                                   3. Try to change the "Destination schema" from "Mirror Source Structure" (if it's set) tp the
                                                   "Destination Default" option.

                                                 More details:
                                                   """;

  public static AbstractBigQueryUploader<?> getUploader(final UploaderConfig uploaderConfig, final AirbyteStreamNameNamespacePair airbyteStreamNameNamespacePair)
      throws IOException {
    final String dataset;
    if (TypingAndDedupingFlag.isDestinationV2()) {
      dataset = uploaderConfig.getParsedStream().id().rawNamespace();
    } else {
      // This previously needed to handle null namespaces. That's now happening at the top of the
      // connector, so we can assume namespace is non-null here.
      dataset = BigQueryUtils.sanitizeDatasetId(uploaderConfig.getConfigStream().getStream().getNamespace());
    }
    final String datasetLocation = BigQueryUtils.getDatasetLocation(uploaderConfig.getConfig());
    final Set<String> existingDatasets = new HashSet<>();

    final BigQueryRecordFormatter recordFormatter = uploaderConfig.getFormatter();
    final Schema bigQuerySchema = recordFormatter.getBigQuerySchema();

    final TableId targetTable = TableId.of(dataset, uploaderConfig.getTargetTableName());
    final TableId tmpTable = TableId.of(dataset, uploaderConfig.getTmpTableName());

    BigQueryUtils.createSchemaAndTableIfNeeded(
        uploaderConfig.getBigQuery(),
        existingDatasets,
        dataset,
        tmpTable,
        datasetLocation,
        bigQuerySchema);

    final JobInfo.WriteDisposition syncMode = BigQueryUtils.getWriteDisposition(
        uploaderConfig.getConfigStream().getDestinationSyncMode());

    return getBigQueryDirectUploader(
        uploaderConfig.getConfig(),
        targetTable,
        tmpTable,
        uploaderConfig.getBigQuery(),
        syncMode,
        datasetLocation,
        recordFormatter,
            airbyteStreamNameNamespacePair);
  }

  private static BigQueryDirectUploader getBigQueryDirectUploader(
                                                                  final JsonNode config,
                                                                  final TableId targetTable,
                                                                  final TableId tmpTable,
                                                                  final BigQuery bigQuery,
                                                                  final JobInfo.WriteDisposition syncMode,
                                                                  final String datasetLocation,
                                                                  final BigQueryRecordFormatter formatter,
                                                                  final AirbyteStreamNameNamespacePair airbyteStreamNameNamespacePair) {
    // https://cloud.google.com/bigquery/docs/loading-data-local#loading_data_from_a_local_data_source
    final TableId tableToWriteRawData = TypingAndDedupingFlag.isDestinationV2() ? targetTable : tmpTable;
    LOGGER.info("is v2: {}", TypingAndDedupingFlag.isDestinationV2());
    LOGGER.info("Will write to dataset " + tableToWriteRawData.getDataset() + " in table " + tableToWriteRawData.getTable() + " in project " + tableToWriteRawData.getProject());
    LOGGER.info("Will write raw data to {} with schema {}", tableToWriteRawData, formatter.getBigQuerySchema());
    final WriteChannelConfiguration writeChannelConfiguration =
        WriteChannelConfiguration.newBuilder(tableToWriteRawData)
            .setCreateDisposition(JobInfo.CreateDisposition.CREATE_IF_NEEDED)
            .setSchema(formatter.getBigQuerySchema())
            .setFormatOptions(FormatOptions.json())
            .build(); // new-line delimited json.

    airbyteStreamNameNamespacePairToJob.putIfAbsent(airbyteStreamNameNamespacePair, UUID.randomUUID().toString());

    final JobId job = JobId.newBuilder()
        .setJob(airbyteStreamNameNamespacePairToJob.get(airbyteStreamNameNamespacePair))
        .setLocation(datasetLocation)
        .setProject(bigQuery.getOptions().getProjectId())
        .build();

    final TableDataWriteChannel writer;

    try {
      writer = bigQuery.writer(job, writeChannelConfiguration);
    } catch (final BigQueryException e) {
      if (e.getCode() == FORBIDDEN || e.getCode() == NOT_FOUND) {
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

    LOGGER.error("----------------- " + writer.toString());

    return new BigQueryDirectUploader(
        targetTable,
        tmpTable,
        new BigQueryTableWriter(writer),
        syncMode,
        bigQuery,
        formatter);
  }

}
