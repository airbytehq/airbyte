/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery;

import com.google.cloud.bigquery.BigQuery;
import com.google.cloud.bigquery.BigQueryException;
import com.google.cloud.bigquery.FormatOptions;
import com.google.cloud.bigquery.Job;
import com.google.cloud.bigquery.JobInfo;
import com.google.cloud.bigquery.JobInfo.WriteDisposition;
import com.google.cloud.bigquery.LoadJobConfiguration;
import com.google.cloud.bigquery.Schema;
import com.google.cloud.bigquery.TableId;
import io.airbyte.commons.exceptions.ConfigErrorException;
import io.airbyte.integrations.destination.StandardNameTransformer;
import io.airbyte.integrations.destination.gcs.GcsDestinationConfig;
import io.airbyte.integrations.destination.gcs.GcsStorageOperations;
import io.airbyte.integrations.destination.record_buffer.SerializableBuffer;
import io.airbyte.integrations.util.ConnectorExceptionUtil;
import java.util.HashSet;
import java.util.List;
import java.util.Set;
import java.util.UUID;
import org.joda.time.DateTime;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class BigQueryGcsOperations implements BigQueryStagingOperations {

  private static final Logger LOGGER = LoggerFactory.getLogger(BigQueryGcsOperations.class);

  private final BigQuery bigQuery;
  private final StandardNameTransformer gcsNameTransformer;
  private final GcsDestinationConfig gcsConfig;
  private final GcsStorageOperations gcsStorageOperations;
  private final UUID randomStagingId;
  private final DateTime syncDatetime;
  private final boolean keepStagingFiles;
  private final Set<String> existingSchemas = new HashSet<>();

  public BigQueryGcsOperations(final BigQuery bigQuery,
                               final StandardNameTransformer gcsNameTransformer,
                               final GcsDestinationConfig gcsConfig,
                               final GcsStorageOperations gcsStorageOperations,
                               final UUID randomStagingId,
                               final DateTime syncDatetime,
                               final boolean keepStagingFiles) {
    this.bigQuery = bigQuery;
    this.gcsNameTransformer = gcsNameTransformer;
    this.gcsConfig = gcsConfig;
    this.gcsStorageOperations = gcsStorageOperations;
    this.randomStagingId = randomStagingId;
    this.syncDatetime = syncDatetime;
    this.keepStagingFiles = keepStagingFiles;
  }

  /**
   * @return {@code <bucket-path>/<dataset-id>_<stream-name>}
   */
  private String getStagingRootPath(final String datasetId, final String stream) {
    return gcsNameTransformer.applyDefaultCase(String.format("%s/%s_%s",
        gcsConfig.getBucketPath(),
        gcsNameTransformer.convertStreamName(datasetId),
        gcsNameTransformer.convertStreamName(stream)));
  }

  /**
   * @return {@code <bucket-path>/<dataset-id>_<stream-name>/<year>/<month>/<day>/<hour>/<uuid>/}
   */
  @Override
  public String getStagingFullPath(final String datasetId, final String stream) {
    return gcsNameTransformer.applyDefaultCase(String.format("%s/%s/%02d/%02d/%02d/%s/",
        getStagingRootPath(datasetId, stream),
        syncDatetime.year().get(),
        syncDatetime.monthOfYear().get(),
        syncDatetime.dayOfMonth().get(),
        syncDatetime.hourOfDay().get(),
        randomStagingId));
  }

  @Override
  public void createSchemaIfNotExists(final String datasetId, final String datasetLocation) {
    if (!existingSchemas.contains(datasetId)) {
      LOGGER.info("Creating dataset {}", datasetId);
      try {
        BigQueryUtils.getOrCreateDataset(bigQuery, datasetId, datasetLocation);
      } catch (final BigQueryException e) {
        if (ConnectorExceptionUtil.HTTP_AUTHENTICATION_ERROR_CODES.contains(e.getCode())) {
          throw new ConfigErrorException(e.getMessage(), e);
        } else {
          throw e;
        }
      }
      existingSchemas.add(datasetId);
    }
  }

  @Override
  public void createTableIfNotExists(final TableId tableId, final Schema tableSchema) {
    LOGGER.info("Creating target table {}", tableId);
    BigQueryUtils.createPartitionedTableIfNotExists(bigQuery, tableId, tableSchema);
  }

  @Override
  public void createStageIfNotExists(final String datasetId, final String stream) {
    final String objectPath = getStagingFullPath(datasetId, stream);
    LOGGER.info("Creating staging path for stream {} (dataset {}): {}", stream, datasetId, objectPath);
    gcsStorageOperations.createBucketIfNotExists();
  }

  @Override
  public String uploadRecordsToStage(final String datasetId, final String stream, final SerializableBuffer writer) {
    final String objectPath = getStagingFullPath(datasetId, stream);
    LOGGER.info("Uploading records to staging for stream {} (dataset {}): {}", stream, datasetId, objectPath);
    return gcsStorageOperations.uploadRecordsToBucket(writer, datasetId, getStagingRootPath(datasetId, stream), objectPath);
  }

  /**
   * Similar to COPY INTO within {@link io.airbyte.integrations.destination.staging.StagingOperations}
   * which loads the data stored in the stage area into a target table in the destination
   *
   * Reference
   * https://googleapis.dev/java/google-cloud-clients/latest/index.html?com/google/cloud/bigquery/package-summary.html
   */
  @Override
  public void copyIntoTableFromStage(final String datasetId,
                                     final String stream,
                                     final TableId tableId,
                                     final Schema tableSchema,
                                     final List<String> stagedFiles) {
    LOGGER.info("Uploading records from staging files to target table {} (dataset {}): {}",
        tableId, datasetId, stagedFiles);

    stagedFiles.parallelStream().forEach(stagedFile -> {
      final String fullFilePath = String.format("gs://%s/%s%s", gcsConfig.getBucketName(), getStagingFullPath(datasetId, stream), stagedFile);
      LOGGER.info("Uploading staged file: {}", fullFilePath);
      final LoadJobConfiguration configuration = LoadJobConfiguration.builder(tableId, fullFilePath)
          .setFormatOptions(FormatOptions.avro())
          .setSchema(tableSchema)
          .setWriteDisposition(WriteDisposition.WRITE_APPEND)
          .setUseAvroLogicalTypes(true)
          .build();

      final Job loadJob = this.bigQuery.create(JobInfo.of(configuration));
      LOGGER.info("[{}] Created a new job to upload record(s) to target table {} (dataset {}): {}", loadJob.getJobId(),
          tableId, datasetId, loadJob);

      try {
        BigQueryUtils.waitForJobFinish(loadJob);
        LOGGER.info("[{}] Target table {} (dataset {}) is successfully appended with staging files", loadJob.getJobId(),
            tableId, datasetId);
      } catch (final BigQueryException | InterruptedException e) {
        throw new RuntimeException(
            String.format("[%s] Failed to upload staging files to destination table %s (%s)", loadJob.getJobId(),
                tableId, datasetId),
            e);
      }
    });
  }

  @Override
  public void cleanUpStage(final String datasetId, final String stream, final List<String> stagedFiles) {
    if (keepStagingFiles) {
      return;
    }

    LOGGER.info("Deleting staging files for stream {} (dataset {}): {}", stream, datasetId, stagedFiles);
    gcsStorageOperations.cleanUpBucketObject(getStagingRootPath(datasetId, stream), stagedFiles);
  }

  @Override
  public void dropTableIfExists(final String datasetId, final TableId tableId) {
    LOGGER.info("Deleting target table {} (dataset {})", tableId, datasetId);
    bigQuery.delete(tableId);
  }

  @Override
  public void dropStageIfExists(final String datasetId, final String stream) {
    if (keepStagingFiles) {
      return;
    }

    final String stagingDatasetPath = getStagingRootPath(datasetId, stream);
    LOGGER.info("Cleaning up staging path for stream {} (dataset {}): {}", stream, datasetId, stagingDatasetPath);
    gcsStorageOperations.dropBucketObject(stagingDatasetPath);
  }

  /**
   * "Truncates" table, this is a workaround to the issue with TRUNCATE TABLE in BigQuery where the
   * table's partition filter must be turned off to truncate. Since deleting a table is a free
   * operation this option re-uses functions that already exist
   *
   * <p>
   * See: https://cloud.google.com/bigquery/pricing#free
   * </p>
   *
   * @param datasetId equivalent to schema name
   * @param tableId table name
   * @param schema schema of the table to be deleted/created
   */
  @Override
  public void truncateTableIfExists(final String datasetId,
                                    final TableId tableId,
                                    final Schema schema) {
    LOGGER.info("Truncating target table {} (dataset {})", tableId, datasetId);
    dropTableIfExists(datasetId, tableId);
    createTableIfNotExists(tableId, schema);
  }

}
