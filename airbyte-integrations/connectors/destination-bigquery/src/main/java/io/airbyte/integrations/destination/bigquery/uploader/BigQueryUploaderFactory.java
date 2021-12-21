/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery.uploader;

import static io.airbyte.integrations.destination.s3.avro.AvroConstants.JSON_CONVERTER;

import com.amazonaws.services.s3.AmazonS3;
import com.fasterxml.jackson.databind.JsonNode;
import com.google.cloud.bigquery.BigQuery;
import com.google.cloud.bigquery.FormatOptions;
import com.google.cloud.bigquery.JobId;
import com.google.cloud.bigquery.JobInfo;
import com.google.cloud.bigquery.Schema;
import com.google.cloud.bigquery.TableDataWriteChannel;
import com.google.cloud.bigquery.TableId;
import com.google.cloud.bigquery.WriteChannelConfiguration;
import io.airbyte.integrations.destination.bigquery.BigQueryUtils;
import io.airbyte.integrations.destination.bigquery.UploadingMethod;
import io.airbyte.integrations.destination.bigquery.formatter.BigQueryRecordFormatter;
import io.airbyte.integrations.destination.bigquery.uploader.config.UploaderConfig;
import io.airbyte.integrations.destination.bigquery.writer.BigQueryTableWriter;
import io.airbyte.integrations.destination.gcs.GcsDestinationConfig;
import io.airbyte.integrations.destination.gcs.GcsS3Helper;
import io.airbyte.integrations.destination.gcs.avro.GcsAvroWriter;
import io.airbyte.protocol.models.ConfiguredAirbyteStream;
import java.io.IOException;
import java.sql.Timestamp;
import java.util.HashSet;
import java.util.Set;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class BigQueryUploaderFactory {

  private static final Logger LOGGER = LoggerFactory.getLogger(BigQueryUploaderFactory.class);

  public static AbstractBigQueryUploader<?> getUploader(UploaderConfig uploaderConfig)
      throws IOException {
    final String schemaName =
        BigQueryUtils.getSchema(uploaderConfig.getConfig(), uploaderConfig.getConfigStream());
    final String datasetLocation = BigQueryUtils.getDatasetLocation(uploaderConfig.getConfig());
    final Set<String> existingSchemas = new HashSet<>();

    final boolean isGcsUploadingMode =
        UploadingMethod.GCS.equals(BigQueryUtils.getLoadingMethod(uploaderConfig.getConfig()));
    BigQueryRecordFormatter recordFormatter =
        (isGcsUploadingMode
            ? uploaderConfig.getFormatterMap().get(UploaderType.AVRO)
            : uploaderConfig.getFormatterMap().get(UploaderType.STANDARD));
    Schema bigQuerySchema = recordFormatter.getBigQuerySchema();

    BigQueryUtils.createSchemaAndTableIfNeeded(
        uploaderConfig.getBigQuery(),
        existingSchemas,
        schemaName,
        uploaderConfig.getTmpTableName(),
        datasetLocation,
        bigQuerySchema);

    final TableId targetTable = TableId.of(schemaName, uploaderConfig.getTargetTableName());
    final TableId tmpTable = TableId.of(schemaName, uploaderConfig.getTmpTableName());
    final JobInfo.WriteDisposition syncMode =
        BigQueryUtils.getWriteDisposition(
            uploaderConfig.getConfigStream().getDestinationSyncMode());

    return (isGcsUploadingMode
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
                                                                       JsonNode config,
                                                                       ConfiguredAirbyteStream configStream,
                                                                       TableId targetTable,
                                                                       TableId tmpTable,
                                                                       BigQuery bigQuery,
                                                                       JobInfo.WriteDisposition syncMode,
                                                                       BigQueryRecordFormatter formatter,
                                                                       boolean isDefaultAirbyteTmpSchema)
      throws IOException {

    final GcsDestinationConfig gcsDestinationConfig =
        GcsDestinationConfig.getGcsDestinationConfig(
            BigQueryUtils.getGcsAvroJsonNodeConfig(config));
    JsonNode tmpTableSchema =
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
                                             final JsonNode bigQuerySchema)
      throws IOException {
    final Timestamp uploadTimestamp = new Timestamp(System.currentTimeMillis());

    final AmazonS3 s3Client = GcsS3Helper.getGcsS3Client(gcsDestinationConfig);
    return new GcsAvroWriter(
        gcsDestinationConfig,
        s3Client,
        configuredStream,
        uploadTimestamp,
        JSON_CONVERTER,
        bigQuerySchema);
  }

  private static BigQueryDirectUploader getBigQueryDirectUploader(
                                                                  JsonNode config,
                                                                  TableId targetTable,
                                                                  TableId tmpTable,
                                                                  BigQuery bigQuery,
                                                                  JobInfo.WriteDisposition syncMode,
                                                                  String datasetLocation,
                                                                  BigQueryRecordFormatter formatter) {
    // https://cloud.google.com/bigquery/docs/loading-data-local#loading_data_from_a_local_data_source
    final WriteChannelConfiguration writeChannelConfiguration =
        WriteChannelConfiguration.newBuilder(tmpTable)
            .setCreateDisposition(JobInfo.CreateDisposition.CREATE_IF_NEEDED)
            .setSchema(formatter.getBigQuerySchema())
            .setFormatOptions(FormatOptions.json())
            .build(); // new-line delimited json.

    final JobId job =
        JobId.newBuilder()
            .setRandomJob()
            .setLocation(datasetLocation)
            .setProject(bigQuery.getOptions().getProjectId())
            .build();

    final TableDataWriteChannel writer = bigQuery.writer(job, writeChannelConfiguration);

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
