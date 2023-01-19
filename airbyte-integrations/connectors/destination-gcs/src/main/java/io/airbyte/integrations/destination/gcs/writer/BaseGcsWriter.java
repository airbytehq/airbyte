/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.gcs.writer;

import com.amazonaws.services.s3.AmazonS3;
import com.amazonaws.services.s3.model.DeleteObjectsRequest.KeyVersion;
import com.amazonaws.services.s3.model.HeadBucketRequest;
import com.amazonaws.services.s3.model.S3ObjectSummary;
import io.airbyte.integrations.destination.gcs.GcsDestinationConfig;
import io.airbyte.integrations.destination.s3.S3DestinationConstants;
import io.airbyte.integrations.destination.s3.S3Format;
import io.airbyte.integrations.destination.s3.util.S3OutputPathHelper;
import io.airbyte.integrations.destination.s3.writer.DestinationFileWriter;
import io.airbyte.protocol.models.v0.AirbyteStream;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.v0.DestinationSyncMode;
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
 * </ul>
 */
public abstract class BaseGcsWriter implements DestinationFileWriter {

  private static final Logger LOGGER = LoggerFactory.getLogger(BaseGcsWriter.class);

  protected final GcsDestinationConfig config;
  protected final AmazonS3 s3Client;
  protected final AirbyteStream stream;
  protected final DestinationSyncMode syncMode;
  protected final String outputPrefix;

  protected BaseGcsWriter(final GcsDestinationConfig config,
                          final AmazonS3 s3Client,
                          final ConfiguredAirbyteStream configuredStream) {
    this.config = config;
    this.s3Client = s3Client;
    this.stream = configuredStream.getStream();
    this.syncMode = configuredStream.getDestinationSyncMode();
    this.outputPrefix = S3OutputPathHelper.getOutputPrefix(config.getBucketPath(), stream);
  }

  /**
   * <ul>
   * <li>1. Create bucket if necessary.</li>
   * <li>2. Under OVERWRITE mode, delete all objects with the output prefix.</li>
   * </ul>
   */
  @Override
  public void initialize() throws IOException {
    try {
      final String bucket = config.getBucketName();
      if (!gcsBucketExist(s3Client, bucket)) {
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
          LOGGER.info("Purging non-empty output path for stream '{}' under OVERWRITE mode...", stream.getName());
          // Google Cloud Storage doesn't accept request to delete multiple objects
          for (final KeyVersion keyToDelete : keysToDelete) {
            s3Client.deleteObject(bucket, keyToDelete.getKey());
          }
          LOGGER.info("Deleted {} file(s) for stream '{}'.", keysToDelete.size(),
              stream.getName());
        }
        LOGGER.info("Overwrite is finished");
      }
    } catch (Exception e) {
      LOGGER.error("Failed to initialize: ", e);
      closeWhenFail();
      throw e;
    }
  }

  /**
   * {@link AmazonS3#doesBucketExistV2} should be used to check the bucket existence. However, this
   * method does not work for GCS. So we use {@link AmazonS3#headBucket} instead, which will throw an
   * exception if the bucket does not exist, or there is no permission to access it.
   */
  public boolean gcsBucketExist(final AmazonS3 s3Client, final String bucket) {
    try {
      s3Client.headBucket(new HeadBucketRequest(bucket));
      return true;
    } catch (final Exception e) {
      return false;
    }
  }

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

  // Filename: <upload-date>_<upload-millis>_0.<format-extension>
  public static String getOutputFilename(final Timestamp timestamp, final S3Format format) {
    final DateFormat formatter = new SimpleDateFormat(S3DestinationConstants.YYYY_MM_DD_FORMAT_STRING);
    formatter.setTimeZone(TimeZone.getTimeZone("UTC"));
    return String.format(
        "%s_%d_0.%s",
        formatter.format(timestamp),
        timestamp.getTime(),
        format.getFileExtension());
  }

}
