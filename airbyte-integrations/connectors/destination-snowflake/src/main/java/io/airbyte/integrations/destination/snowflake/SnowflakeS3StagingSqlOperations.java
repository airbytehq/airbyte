/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake;

import alex.mojaki.s3upload.MultiPartOutputStream;
import alex.mojaki.s3upload.StreamTransferManager;
import com.amazonaws.services.s3.AmazonS3;
import com.amazonaws.services.s3.model.DeleteObjectsRequest;
import com.amazonaws.services.s3.model.DeleteObjectsRequest.KeyVersion;
import com.amazonaws.services.s3.model.ObjectListing;
import io.airbyte.commons.lang.Exceptions;
import io.airbyte.commons.string.Strings;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.destination.NamingConventionTransformer;
import io.airbyte.integrations.destination.buffered_stream_consumer.RecordBufferImplementation;
import io.airbyte.integrations.destination.s3.S3DestinationConfig;
import io.airbyte.integrations.destination.s3.util.S3StreamTransferManagerHelper;
import io.airbyte.integrations.destination.staging.StagingOperations;
import java.io.InputStream;
import java.util.ArrayList;
import java.util.List;
import java.util.StringJoiner;
import org.joda.time.DateTime;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class SnowflakeS3StagingSqlOperations extends SnowflakeSqlOperations implements StagingOperations {

  private static final Logger LOGGER = LoggerFactory.getLogger(SnowflakeSqlOperations.class);
  private static final int DEFAULT_UPLOAD_THREADS = 10; // The S3 cli uses 10 threads by default.
  private static final int DEFAULT_QUEUE_CAPACITY = DEFAULT_UPLOAD_THREADS;
  private static final int DEFAULT_PART_SIZE = 10;
  private static final int UPLOAD_RETRY_LIMIT = 3;

  private final NamingConventionTransformer nameTransformer;
  private final S3DestinationConfig s3Config;
  private AmazonS3 s3Client;

  public SnowflakeS3StagingSqlOperations(final NamingConventionTransformer nameTransformer,
                                         final AmazonS3 s3Client,
                                         final S3DestinationConfig s3Config) {
    this.nameTransformer = nameTransformer;
    this.s3Client = s3Client;
    this.s3Config = s3Config;
  }

  @Override
  public String getStageName(final String namespace, final String streamName) {
    return nameTransformer.applyDefaultCase(String.join("_",
        nameTransformer.convertStreamName(namespace),
        nameTransformer.convertStreamName(streamName)));
  }

  @Override
  public String getStagingPath(final String connectionId, final String namespace, final String streamName, final DateTime writeDatetime) {
    // see https://docs.snowflake.com/en/user-guide/data-load-considerations-stage.html
    return nameTransformer.applyDefaultCase(String.format("%s/%s/%s/%02d/%02d/%02d/",
        connectionId,
        getStageName(namespace, streamName),
        writeDatetime.year().get(),
        writeDatetime.monthOfYear().get(),
        writeDatetime.dayOfMonth().get(),
        writeDatetime.hourOfDay().get()));
  }

  @Override
  public String uploadRecordsToStage(final JdbcDatabase database,
                                     final RecordBufferImplementation recordsData,
                                     final String schemaName,
                                     final String path) {
    final List<Exception> exceptionsThrown = new ArrayList<>();
    boolean succeeded = false;
    while (exceptionsThrown.size() < UPLOAD_RETRY_LIMIT && !succeeded) {
      try {
        loadDataIntoStage(path, recordsData);
        succeeded = true;
      } catch (final Exception e) {
        LOGGER.error("Failed to upload records into stage {}", path, e);
        exceptionsThrown.add(e);
      }
      if (!succeeded) {
        LOGGER.info("Retrying to upload records into stage {} ({}/{}})", path, exceptionsThrown.size(), UPLOAD_RETRY_LIMIT);
        // Force a reconnection before retrying in case error was due to network issues...
        s3Client = s3Config.resetS3Client();
      }
    }
    if (!succeeded) {
      throw new RuntimeException(String.format("Exceptions thrown while uploading records into stage: %s", Strings.join(exceptionsThrown, "\n")));
    }
    return recordsData.getFilename();
  }

  private void loadDataIntoStage(final String stage, final RecordBufferImplementation recordsData) {
    final long partSize = s3Config.getFormatConfig() != null ? s3Config.getFormatConfig().getPartSize() : DEFAULT_PART_SIZE;
    final String bucket = s3Config.getBucketName();
    final String objectKey = String.format("%s%s", stage, recordsData.getFilename());
    final StreamTransferManager uploadManager = S3StreamTransferManagerHelper
        .getDefault(bucket, objectKey, s3Client, partSize)
        .checkIntegrity(true)
        .numUploadThreads(DEFAULT_UPLOAD_THREADS)
        .queueCapacity(DEFAULT_QUEUE_CAPACITY);
    boolean hasFailed = false;
    try {
      final List<MultiPartOutputStream> outputStreams = uploadManager.getMultiPartOutputStreams();
      try (final MultiPartOutputStream outputStream = outputStreams.get(0)) {
        try (final InputStream dataStream = recordsData.getInputStream()) {
          dataStream.transferTo(outputStream);
        }
      }
    } catch (final Exception e) {
      LOGGER.error("Failed to load data into stage {}", stage, e);
      hasFailed = true;
      throw new RuntimeException(e);
    } finally {
      if (hasFailed) {
        uploadManager.abort();
      } else {
        uploadManager.complete();
      }
    }
    if (!s3Client.doesObjectExist(bucket, objectKey)) {
      LOGGER.error("Failed to upload data into stage, object {} not found", objectKey);
      throw new RuntimeException("Upload failed");
    }
  }

  @Override
  public void createStageIfNotExists(final JdbcDatabase database, final String stageName) {
    final String bucket = s3Config.getBucketName();
    if (!s3Client.doesBucketExistV2(bucket)) {
      LOGGER.info("Bucket {} does not exist; creating...", bucket);
      s3Client.createBucket(bucket);
      LOGGER.info("Bucket {} has been created.", bucket);
    }
    if (!s3Client.doesObjectExist(bucket, stageName)) {
      LOGGER.info("Stage {}/{} does not exist; creating...", bucket, stageName);
      s3Client.putObject(bucket, stageName.endsWith("/") ? stageName : stageName + "/", "");
      LOGGER.info("Stage {}/{} has been created.", bucket, stageName);
    }
  }

  @Override
  public void copyIntoTmpTableFromStage(final JdbcDatabase database,
                                        final String stageName,
                                        final List<String> stagedFiles,
                                        final String dstTableName,
                                        final String schemaName) {
    LOGGER.info("Starting copy to tmp table from stage: {} in destination from stage: {}, schema: {}, .", dstTableName, stageName, schemaName);
    final var copyQuery = String.format(
        "COPY INTO %s.%s FROM '%s' "
            + "CREDENTIALS=(aws_key_id='%s' aws_secret_key='%s') "
            + "file_format = (type = csv compression = auto field_delimiter = ',' skip_header = 0 FIELD_OPTIONALLY_ENCLOSED_BY = '\"');",
        schemaName,
        dstTableName,
        generateBucketPath(stageName),
        s3Config.getAccessKeyId(),
        s3Config.getSecretAccessKey());
    LOGGER.info(copyQuery);
    Exceptions.toRuntime(() -> database.execute(copyQuery));
    LOGGER.info("Copy to tmp table {}.{} in destination complete.", schemaName, dstTableName);
  }

  private String generateBucketPath(final String stage) {
    return "s3://" + s3Config.getBucketName() + "/" + stage;
  }

  private String generateFilesList(final List<String> files) {
    final StringJoiner joiner = new StringJoiner(",");
    files.forEach(filename -> joiner.add("'" + filename.substring(filename.lastIndexOf("/") + 1) + "'"));
    return joiner.toString();
  }

  @Override
  public void dropStageIfExists(final JdbcDatabase database, final String stageName) {
    LOGGER.info("Dropping stage {}...", stageName);
    final String bucket = s3Config.getBucketName();
    if (s3Client.doesObjectExist(bucket, stageName)) {
      s3Client.deleteObject(bucket, stageName);
    }
    LOGGER.info("Stage object {} has been deleted...", stageName);
  }

  @Override
  public void cleanUpStage(final JdbcDatabase database, final String stageName, final List<String> stagedFiles) {
    final String bucket = s3Config.getBucketName();
    ObjectListing objects = s3Client.listObjects(bucket, stageName);
    while (objects.isTruncated()) {
      if (objects.getObjectSummaries().size() > 0) {
        final List<KeyVersion> toDelete = objects.getObjectSummaries()
            .stream()
            .filter(obj -> stagedFiles.isEmpty() || stagedFiles.contains(obj.getKey()))
            .map(obj -> new KeyVersion(obj.getKey()))
            .toList();
        s3Client.deleteObjects(new DeleteObjectsRequest(bucket).withKeys(toDelete));
        LOGGER.info("Stage {} has been clean-up ({} objects were deleted)...", stageName, toDelete.size());
      }
      objects = s3Client.listNextBatchOfObjects(objects);
    }
  }

}
