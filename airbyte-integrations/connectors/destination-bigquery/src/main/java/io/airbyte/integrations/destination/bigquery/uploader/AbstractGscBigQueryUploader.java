/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery.uploader;

import com.amazonaws.services.s3.AmazonS3;
import com.amazonaws.services.s3.model.DeleteObjectsRequest;
import com.amazonaws.services.s3.model.S3ObjectSummary;
import com.google.cloud.bigquery.BigQuery;
import com.google.cloud.bigquery.BigQueryException;
import com.google.cloud.bigquery.Job;
import com.google.cloud.bigquery.JobInfo;
import com.google.cloud.bigquery.JobInfo.WriteDisposition;
import com.google.cloud.bigquery.LoadJobConfiguration;
import com.google.cloud.bigquery.TableId;
import io.airbyte.integrations.destination.bigquery.BigQueryUtils;
import io.airbyte.integrations.destination.bigquery.formatter.BigQueryRecordFormatter;
import io.airbyte.integrations.destination.gcs.GcsDestinationConfig;
import io.airbyte.integrations.destination.s3.writer.DestinationFileWriter;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import java.util.List;
import java.util.function.Consumer;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public abstract class AbstractGscBigQueryUploader<T extends DestinationFileWriter> extends AbstractBigQueryUploader<DestinationFileWriter> {

  private static final Logger LOGGER = LoggerFactory.getLogger(AbstractGscBigQueryUploader.class);

  private final boolean isKeepFilesInGcs;
  protected final GcsDestinationConfig gcsDestinationConfig;

  AbstractGscBigQueryUploader(final TableId table,
                              final TableId tmpTable,
                              final T writer,
                              final WriteDisposition syncMode,
                              final GcsDestinationConfig gcsDestinationConfig,
                              final BigQuery bigQuery,
                              final boolean isKeepFilesInGcs,
                              final BigQueryRecordFormatter recordFormatter) {
    super(table, tmpTable, writer, syncMode, bigQuery, recordFormatter);
    this.isKeepFilesInGcs = isKeepFilesInGcs;
    this.gcsDestinationConfig = gcsDestinationConfig;
  }

  @Override
  public void postProcessAction(final boolean hasFailed) {
    if (!isKeepFilesInGcs) {
      deleteGcsFiles();
    }
  }

  @Override
  protected void uploadData(final Consumer<AirbyteMessage> outputRecordCollector, final AirbyteMessage lastStateMessage) throws Exception {
    LOGGER.info("Uploading data to the tmp table {}.", tmpTable.getTable());
    uploadDataFromFileToTmpTable();
    super.uploadData(outputRecordCollector, lastStateMessage);
  }

  protected void uploadDataFromFileToTmpTable() {
    try {
      final String fileLocation = this.writer.getFileLocation();

      // Initialize client that will be used to send requests. This client only needs to be created
      // once, and can be reused for multiple requests.
      LOGGER.info(String.format("Started copying data from %s GCS " + getFileTypeName() + " file to %s tmp BigQuery table with schema: \n %s",
          fileLocation, tmpTable, recordFormatter.getBigQuerySchema()));

      final LoadJobConfiguration configuration = getLoadConfiguration();

      // For more information on Job see:
      // https://googleapis.dev/java/google-cloud-clients/latest/index.html?com/google/cloud/bigquery/package-summary.html
      // Load the table
      final Job loadJob = this.bigQuery.create(JobInfo.of(configuration));
      LOGGER.info("Created a new job GCS " + getFileTypeName() + " file to tmp BigQuery table: " + loadJob);

      // Load data from a GCS parquet file into the table
      // Blocks until this load table job completes its execution, either failing or succeeding.
      BigQueryUtils.waitForJobFinish(loadJob);

      LOGGER.info("Table is successfully overwritten by file loaded from GCS: {}", getFileTypeName());
    } catch (final BigQueryException | InterruptedException e) {
      LOGGER.error("Column not added during load append", e);
      throw new RuntimeException("Column not added during load append \n" + e.toString());
    }
  }

  abstract protected LoadJobConfiguration getLoadConfiguration();

  private String getFileTypeName() {
    return writer.getFileFormat().getFileExtension();
  }

  private void deleteGcsFiles() {
    LOGGER.info("Deleting file {}", writer.getFileLocation());
    final GcsDestinationConfig gcsDestinationConfig = this.gcsDestinationConfig;
    final AmazonS3 s3Client = gcsDestinationConfig.getS3Client();

    final String gcsBucketName = gcsDestinationConfig.getBucketName();
    final String gcs_bucket_path = gcsDestinationConfig.getBucketPath();

    final List<S3ObjectSummary> objects = s3Client
        .listObjects(gcsBucketName, gcs_bucket_path)
        .getObjectSummaries();

    objects.stream().filter(s3ObjectSummary -> s3ObjectSummary.getKey().equals(writer.getOutputPath())).forEach(s3ObjectSummary -> {
      s3Client.deleteObject(gcsBucketName, new DeleteObjectsRequest.KeyVersion(s3ObjectSummary.getKey()).getKey());
      LOGGER.info("File is deleted : " + s3ObjectSummary.getKey());
    });
    s3Client.shutdown();
  }

}
