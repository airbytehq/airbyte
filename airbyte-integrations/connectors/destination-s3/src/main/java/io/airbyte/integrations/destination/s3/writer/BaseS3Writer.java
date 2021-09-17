/*
 * MIT License
 *
 * Copyright (c) 2020 Airbyte
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
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
 * <li>Create shared instance variables.</li>
 * <li>Create the bucket and prepare the bucket path.</li>
 * <li>Log and close the write.</li>
 */
public abstract class BaseS3Writer implements S3Writer {

  private static final Logger LOGGER = LoggerFactory.getLogger(BaseS3Writer.class);

  protected final S3DestinationConfig config;
  protected final AmazonS3 s3Client;
  protected final AirbyteStream stream;
  protected final DestinationSyncMode syncMode;
  protected final String outputPrefix;

  protected BaseS3Writer(S3DestinationConfig config,
                         AmazonS3 s3Client,
                         ConfiguredAirbyteStream configuredStream) {
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
   * <li>1. Create bucket if necessary.</li>
   * <li>2. Under OVERWRITE mode, delete all objects with the output prefix.</li>
   */
  @Override
  public void initialize() {
    String bucket = config.getBucketName();
    if (!s3Client.doesBucketExistV2(bucket)) {
      LOGGER.info("Bucket {} does not exist; creating...", bucket);
      s3Client.createBucket(bucket);
      LOGGER.info("Bucket {} has been created.", bucket);
    }

    if (syncMode == DestinationSyncMode.OVERWRITE) {
      LOGGER.info("Overwrite mode");
      List<KeyVersion> keysToDelete = new LinkedList<>();
      List<S3ObjectSummary> objects = s3Client.listObjects(bucket, outputPrefix)
          .getObjectSummaries();
      for (S3ObjectSummary object : objects) {
        keysToDelete.add(new KeyVersion(object.getKey()));
      }

      if (keysToDelete.size() > 0) {
        LOGGER.info("Purging non-empty output path for stream '{}' under OVERWRITE mode...",
            stream.getName());
        DeleteObjectsResult result = s3Client
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
  public void close(boolean hasFailed) throws IOException {
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
  public static String getOutputFilename(Timestamp timestamp, S3Format format) {
    DateFormat formatter = new SimpleDateFormat(S3DestinationConstants.YYYY_MM_DD_FORMAT_STRING);
    formatter.setTimeZone(TimeZone.getTimeZone("UTC"));
    return String.format(
        "%s_%d_0.%s",
        formatter.format(timestamp),
        timestamp.getTime(),
        format.getFileExtension());
  }

}
