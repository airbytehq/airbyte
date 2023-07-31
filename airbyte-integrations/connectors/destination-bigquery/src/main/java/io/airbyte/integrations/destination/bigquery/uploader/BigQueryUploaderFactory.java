/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery.uploader;

import static io.airbyte.integrations.destination.s3.avro.AvroConstants.JSON_CONVERTER;
import static software.amazon.awssdk.http.HttpStatusCode.FORBIDDEN;
import static software.amazon.awssdk.http.HttpStatusCode.NOT_FOUND;

import com.amazonaws.services.s3.AmazonS3;
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
import io.airbyte.integrations.destination.gcs.GcsDestinationConfig;
import io.airbyte.integrations.destination.gcs.avro.GcsAvroWriter;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import java.io.IOException;
import java.sql.Timestamp;
import java.util.HashSet;
import java.util.Set;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class BigQueryUploaderFactory {

  private static final Logger LOGGER = LoggerFactory.getLogger(BigQueryUploaderFactory.class);

  private static final String CONFIG_ERROR_MSG = """
                                                    Failed to write to destination schema.

                                                   1. Make sure you have all required permissions for writing to the schema.

                                                   2. Make sure that the actual destination schema's location corresponds to location provided
                                                     in connector's config.

                                                   3. Try to change the "Destination schema" from "Mirror Source Structure" (if it's set) tp the
                                                   "Destination Default" option.

                                                 More details:
                                                   """;

  public static AbstractBigQueryUploader<?> getUploader(final UploaderConfig uploaderConfig)
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

    return (uploaderConfig.isGcsUploadingMode()
        ? getGcsBigQueryUploader(
            uploaderConfig.getConfig(),
            uploaderConfig.getConfigStream(),
            targetTable,
            tmpTable,
            uploaderConfig.getBigQuery(),
            syncMode,
            recordFormatter,
            uploaderConfig.isDefaultAirbyteTmpSchema())
        : getBigQueryDirectUploader(
            uploaderConfig.getConfig(),
            targetTable,
            tmpTable,
            uploaderConfig.getBigQuery(),
            syncMode,
            datasetLocation,
            recordFormatter));
  }

  private static AbstractGscBigQueryUploader<?> getGcsBigQueryUploader(
                                                                       final JsonNode config,
                                                                       final ConfiguredAirbyteStream configStream,
                                                                       final TableId targetTable,
                                                                       final TableId tmpTable,
                                                                       final BigQuery bigQuery,
                                                                       final JobInfo.WriteDisposition syncMode,
                                                                       final BigQueryRecordFormatter formatter,
                                                                       final boolean isDefaultAirbyteTmpSchema)
      throws IOException {

    final GcsDestinationConfig gcsDestinationConfig = BigQueryUtils.getGcsAvroDestinationConfig(config);
    final JsonNode tmpTableSchema =
        (isDefaultAirbyteTmpSchema ? null : formatter.getJsonSchema());
    final GcsAvroWriter gcsCsvWriter =
        initGcsWriter(gcsDestinationConfig, configStream, tmpTableSchema);
    gcsCsvWriter.initialize();

    return new GcsAvroBigQueryUploader(
        targetTable,
        tmpTable,
        gcsCsvWriter,
        syncMode,
        gcsDestinationConfig,
        bigQuery,
        BigQueryUtils.isKeepFilesInGcs(config),
        formatter);
  }

  private static GcsAvroWriter initGcsWriter(
                                             final GcsDestinationConfig gcsDestinationConfig,
                                             final ConfiguredAirbyteStream configuredStream,
                                             final JsonNode jsonSchema)
      throws IOException {
    final Timestamp uploadTimestamp = new Timestamp(System.currentTimeMillis());

    final AmazonS3 s3Client = gcsDestinationConfig.getS3Client();
    return new GcsAvroWriter(
        gcsDestinationConfig,
        s3Client,
        configuredStream,
        uploadTimestamp,
        JSON_CONVERTER,
        jsonSchema);
  }

  private static BigQueryDirectUploader getBigQueryDirectUploader(
                                                                  final JsonNode config,
                                                                  final TableId targetTable,
                                                                  final TableId tmpTable,
                                                                  final BigQuery bigQuery,
                                                                  final JobInfo.WriteDisposition syncMode,
                                                                  final String datasetLocation,
                                                                  final BigQueryRecordFormatter formatter) {
    // https://cloud.google.com/bigquery/docs/loading-data-local#loading_data_from_a_local_data_source
    final TableId tableToWriteRawData = TypingAndDedupingFlag.isDestinationV2() ? targetTable : tmpTable;
    LOGGER.info("Will write raw data to {} with schema {}", tableToWriteRawData, formatter.getBigQuerySchema());
    final WriteChannelConfiguration writeChannelConfiguration =
        WriteChannelConfiguration.newBuilder(tableToWriteRawData)
            .setCreateDisposition(JobInfo.CreateDisposition.CREATE_IF_NEEDED)
            .setSchema(formatter.getBigQuerySchema())
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

    return new BigQueryDirectUploader(
        targetTable,
        tmpTable,
        new BigQueryTableWriter(writer),
        syncMode,
        bigQuery,
        formatter);
  }

}
