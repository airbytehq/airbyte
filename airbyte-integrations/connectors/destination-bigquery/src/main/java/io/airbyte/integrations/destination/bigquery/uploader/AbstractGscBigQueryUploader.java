/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery.uploader;

import com.amazonaws.services.s3.AmazonS3;
import com.amazonaws.services.s3.model.DeleteObjectsRequest;
import com.amazonaws.services.s3.model.S3ObjectSummary;
import com.google.cloud.bigquery.*;
import com.google.cloud.bigquery.JobInfo.WriteDisposition;
import io.airbyte.integrations.destination.gcs.GcsDestinationConfig;
import io.airbyte.integrations.destination.gcs.GcsS3Helper;
import io.airbyte.integrations.destination.gcs.writer.GscWriter;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.LinkedList;
import java.util.List;

public abstract class AbstractGscBigQueryUploader<T extends GscWriter> extends AbstractBigQueryUploader<GscWriter> {

  private static final Logger LOGGER = LoggerFactory.getLogger(AbstractGscBigQueryUploader.class);

  private final boolean isKeepFilesInGcs;

  AbstractGscBigQueryUploader(final TableId table,
                              final TableId tmpTable,
                              final T writer,
                              final WriteDisposition syncMode,
                              final Schema schema,
                              final GcsDestinationConfig gcsDestinationConfig,
                              final BigQuery bigQuery,
                              final boolean isKeepFilesInGcs) {
    super(table, tmpTable, writer, syncMode, schema, gcsDestinationConfig, bigQuery);
    this.isKeepFilesInGcs = isKeepFilesInGcs;
  }

  @Override
  public void closeWriter(boolean hasFailed) throws Exception {
    writer.close(hasFailed);
    // copy data from tmp gcs storage to bigquery tables
    try {
      loadCsvFromGcsTruncate();
    } catch (final Exception e) {
      LOGGER.error("Failed to load data from GCS "+getFileTypeName()+" file to BigQuery tmp table with reason: " + e.getMessage());
      throw new RuntimeException(e);
    }
  }

  abstract protected LoadJobConfiguration getLoadConfiguration();

  private void loadCsvFromGcsTruncate()
          throws Exception {
    try {
      final String fileLocation = this.writer.getFileLocation();

      // Initialize client that will be used to send requests. This client only needs to be created
      // once, and can be reused for multiple requests.
      LOGGER.info(String.format("Started copying data from %s GCS "+getFileTypeName()+" file to %s tmp BigQuery table with schema: \n %s",
              fileLocation, tmpTable, schema));

      LoadJobConfiguration configuration = getLoadConfiguration();

      // For more information on Job see:
      // https://googleapis.dev/java/google-cloud-clients/latest/index.html?com/google/cloud/bigquery/package-summary.html
      // Load the table
      final Job loadJob = this.bigQuery.create(JobInfo.of(configuration));

      LOGGER.info("Created a new job GCS "+getFileTypeName()+" file to tmp BigQuery table: " + loadJob);
      LOGGER.info("Waiting for job to complete...");

      // Load data from a GCS parquet file into the table
      // Blocks until this load table job completes its execution, either failing or succeeding.
      final Job completedJob = loadJob.waitFor();

      // Check for errors
      if (completedJob == null) {
        LOGGER.error("Job not executed since it no longer exists.");
        throw new Exception("Job not executed since it no longer exists.");
      } else if (completedJob.getStatus().getError() != null) {
        // You can also look at queryJob.getStatus().getExecutionErrors() for all
        // errors, not just the latest one.
        final String msg = "BigQuery was unable to load into the table due to an error: \n"
                + loadJob.getStatus().getError();
        LOGGER.error(msg);
        throw new Exception(msg);
      }
      LOGGER.info("Table is successfully overwritten by "+getFileTypeName()+" file loaded from GCS");
    } catch (final BigQueryException | InterruptedException e) {
      LOGGER.error("Column not added during load append \n" + e.toString());
      throw new RuntimeException("Column not added during load append \n" + e.toString());
    } finally {
      if (isKeepFilesInGcs)
        deleteGcsFiles();
    }
  }

  private String getFileTypeName() {
    return writer.getFileFormat().getFileExtension();
  }

  private void deleteGcsFiles() {
    LOGGER.info("Deleting file {}", writer.getFileLocation());
    final GcsDestinationConfig gcsDestinationConfig = this.gcsDestinationConfig;
    final AmazonS3 s3Client = GcsS3Helper.getGcsS3Client(gcsDestinationConfig);

    final String gcsBucketName = gcsDestinationConfig.getBucketName();
    final String gcs_bucket_path = gcsDestinationConfig.getBucketPath();

    final List<DeleteObjectsRequest.KeyVersion> keysToDelete = new LinkedList<>();
    final List<S3ObjectSummary> objects = s3Client
            .listObjects(gcsBucketName, gcs_bucket_path)
            .getObjectSummaries();
    for (final S3ObjectSummary object : objects) {
      keysToDelete.add(new DeleteObjectsRequest.KeyVersion(object.getKey()));
    }

    if (!keysToDelete.isEmpty()) {
      LOGGER.info("Tearing down test bucket path: {}/{}", gcsBucketName, gcs_bucket_path);
      // Google Cloud Storage doesn't accept request to delete multiple objects
      for (final DeleteObjectsRequest.KeyVersion keyToDelete : keysToDelete) {
        s3Client.deleteObject(gcsBucketName, keyToDelete.getKey());
      }
      LOGGER.info("Deleted {} file(s).", keysToDelete.size());
    }
    s3Client.shutdown();
  }
}
