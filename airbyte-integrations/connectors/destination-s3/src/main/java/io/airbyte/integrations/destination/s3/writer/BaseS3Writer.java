/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3.writer;

import com.amazonaws.services.s3.AmazonS3;
import com.amazonaws.services.s3.model.DeleteObjectsRequest;
import com.amazonaws.services.s3.model.DeleteObjectsRequest.KeyVersion;
import com.amazonaws.services.s3.model.DeleteObjectsResult;
import com.amazonaws.services.s3.model.S3ObjectSummary;
import io.airbyte.integrations.destination.s3.S3DestinationConfig;
import io.airbyte.integrations.destination.s3.S3DestinationConstants;
import io.airbyte.integrations.destination.s3.S3Format;
import io.airbyte.integrations.destination.s3.util.S3OutputPathHelper;
import io.airbyte.protocol.models.AirbyteStream;
import io.airbyte.protocol.models.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.DestinationSyncMode;
import java.io.IOException;
import java.sql.Timestamp;
import java.text.DateFormat;
import java.text.SimpleDateFormat;
import java.util.LinkedList;
import java.util.List;
import java.util.TimeZone;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * The base implementation takes care of the following:
 * <ul>
 * <li>Create shared instance variables.</li>
 * <li>Create the bucket and prepare the bucket path.</li>
 * <li>Log and close the write.</li>
 * </ul>
 */
public abstract class BaseS3Writer implements DestinationFileWriter {

  private static final Logger LOGGER = LoggerFactory.getLogger(BaseS3Writer.class);
  private static final String DEFAULT_SUFFIX = "_0";

  protected final S3DestinationConfig config;
  protected final AmazonS3 s3Client;
  protected final AirbyteStream stream;
  protected final DestinationSyncMode syncMode;
  protected final String outputPrefix;

  protected BaseS3Writer(final S3DestinationConfig config,
                         final AmazonS3 s3Client,
                         final ConfiguredAirbyteStream configuredStream) {
    this.config = config;
    this.s3Client = s3Client;
    this.stream = configuredStream.getStream();
    this.syncMode = configuredStream.getDestinationSyncMode();
    this.outputPrefix = S3OutputPathHelper.getOutputPrefix(config.getBucketPath(), stream);
  }

  public String getOutputPrefix() {
    return outputPrefix;
  }

  /**
   * <ul>
   * <li>1. Create bucket if necessary.</li>
   * <li>2. Under OVERWRITE mode, delete all objects with the output prefix.</li>
   * </ul>
   */
  @Override
  public void initialize() {
    final String bucket = config.getBucketName();
    if (!s3Client.doesBucketExistV2(bucket)) {
      LOGGER.info("Bucket {} does not exist; creating...", bucket);
      s3Client.createBucket(bucket);
      LOGGER.info("Bucket {} has been created.", bucket);
    }

    if (syncMode == DestinationSyncMode.OVERWRITE) {
      LOGGER.info("Overwrite mode");
      final List<KeyVersion> keysToDelete = new LinkedList<>();
      final List<S3ObjectSummary> objects = s3Client.listObjects(bucket, outputPrefix)
          .getObjectSummaries();
      for (final S3ObjectSummary object : objects) {
        keysToDelete.add(new KeyVersion(object.getKey()));
      }

      if (keysToDelete.size() > 0) {
        LOGGER.info("Purging non-empty output path for stream '{}' under OVERWRITE mode...",
            stream.getName());
        final DeleteObjectsResult result = s3Client
            .deleteObjects(new DeleteObjectsRequest(bucket).withKeys(keysToDelete));
        LOGGER.info("Deleted {} file(s) for stream '{}'.", result.getDeletedObjects().size(),
            stream.getName());
      }
    }
  }

  /**
   * Log and close the write.
   */
  @Override
  public void close(final boolean hasFailed) throws IOException {
    if (hasFailed) {
      LOGGER.warn("Failure detected. Aborting upload of stream '{}'...", stream.getName());
      closeWhenFail();
      LOGGER.warn("Upload of stream '{}' aborted.", stream.getName());
    } else {
      LOGGER.info("Uploading remaining data for stream '{}'.", stream.getName());
      closeWhenSucceed();
      LOGGER.info("Upload completed for stream '{}'.", stream.getName());
    }
  }

  /**
   * Operations that will run when the write succeeds.
   */
  protected void closeWhenSucceed() throws IOException {
    // Do nothing by default
  }

  /**
   * Operations that will run when the write fails.
   */
  protected void closeWhenFail() throws IOException {
    // Do nothing by default
  }

  /**
   * @return A string in the format "{upload-date}_{upload-millis}_0.{format-extension}". For example,
   *         "2021_12_09_1639077474000_0.csv"
   */
  public static String getOutputFilename(final Timestamp timestamp, final S3Format format) {
    return getOutputFilename(timestamp, DEFAULT_SUFFIX, format);
  }

  /**
   * @param customSuffix A string to append to the filename. Commonly used to distinguish multiple
   *        part files within a single upload. You probably want to use strings with a leading
   *        underscore (i.e. prefer "_0" to "0").
   * @return A string in the format "{upload-date}_{upload-millis}_{suffix}.{format-extension}". For
   *         example, "2021_12_09_1639077474000_customSuffix.csv"
   */
  public static String getOutputFilename(final Timestamp timestamp, final String customSuffix, final S3Format format) {
    final DateFormat formatter = new SimpleDateFormat(S3DestinationConstants.YYYY_MM_DD_FORMAT_STRING);
    formatter.setTimeZone(TimeZone.getTimeZone("UTC"));
    return String.format(
        "%s_%d%s.%s",
        formatter.format(timestamp),
        timestamp.getTime(),
        customSuffix,
        format.getFileExtension());
  }

}
