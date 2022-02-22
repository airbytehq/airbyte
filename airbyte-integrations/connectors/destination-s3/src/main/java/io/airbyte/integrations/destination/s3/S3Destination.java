/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3;

import alex.mojaki.s3upload.MultiPartOutputStream;
import alex.mojaki.s3upload.StreamTransferManager;
import com.amazonaws.services.s3.AmazonS3;
import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.annotations.VisibleForTesting;
import io.airbyte.integrations.BaseConnector;
import io.airbyte.integrations.base.AirbyteMessageConsumer;
import io.airbyte.integrations.base.Destination;
import io.airbyte.integrations.base.IntegrationRunner;
import io.airbyte.integrations.destination.s3.util.S3StreamTransferManagerHelper;
import io.airbyte.integrations.destination.s3.writer.ProductionWriterFactory;
import io.airbyte.integrations.destination.s3.writer.S3WriterFactory;
import io.airbyte.protocol.models.AirbyteConnectionStatus;
import io.airbyte.protocol.models.AirbyteConnectionStatus.Status;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import java.io.IOException;
import java.io.PrintWriter;
import java.nio.charset.StandardCharsets;
import java.util.UUID;
import java.util.function.Consumer;
import org.apache.commons.csv.CSVFormat;
import org.apache.commons.csv.CSVPrinter;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class S3Destination extends BaseConnector implements Destination {

  private static final Logger LOGGER = LoggerFactory.getLogger(S3Destination.class);

  public static void main(final String[] args) throws Exception {
    new IntegrationRunner(new S3Destination()).run(args);
  }

  @Override
  public AirbyteConnectionStatus check(final JsonNode config) {
    try {
      final S3DestinationConfig destinationConfig = S3DestinationConfig.getS3DestinationConfig(config);
      final AmazonS3 s3Client = destinationConfig.getS3Client();

      // Test single upload (for small files) permissions
      testSingleUpload(s3Client, destinationConfig.getBucketName());

      // Test multipart upload with stream transfer manager
      testMultipartUpload(s3Client, destinationConfig.getBucketName());

      return new AirbyteConnectionStatus().withStatus(Status.SUCCEEDED);
    } catch (final Exception e) {
      LOGGER.error("Exception attempting to access the S3 bucket: ", e);
      return new AirbyteConnectionStatus()
          .withStatus(AirbyteConnectionStatus.Status.FAILED)
          .withMessage("Could not connect to the S3 bucket with the provided configuration. \n" + e
              .getMessage());
    }
  }

  public static void testSingleUpload(final AmazonS3 s3Client, final String bucketName) {
    LOGGER.info("Started testing if all required credentials assigned to user for single file uploading");
    final String testFile = "test_" + System.currentTimeMillis();
    s3Client.putObject(bucketName, testFile, "this is a test file");
    s3Client.deleteObject(bucketName, testFile);
    LOGGER.info("Finished checking for normal upload mode");
  }

  public static void testMultipartUpload(final AmazonS3 s3Client, final String bucketName) throws IOException {
    LOGGER.info("Started testing if all required credentials assigned to user for multipart upload");

    final String testFile = "test_" + System.currentTimeMillis();
    final StreamTransferManager manager = S3StreamTransferManagerHelper.getDefault(
        bucketName,
        testFile,
        s3Client,
        (long) S3StreamTransferManagerHelper.DEFAULT_PART_SIZE_MB);

    try (final MultiPartOutputStream outputStream = manager.getMultiPartOutputStreams().get(0);
        final CSVPrinter csvPrinter = new CSVPrinter(new PrintWriter(outputStream, true, StandardCharsets.UTF_8), CSVFormat.DEFAULT)) {
      final String oneMegaByteString = "a".repeat(500_000);
      // write a file larger than the 5 MB, which is the default part size, to make sure it is a multipart
      // upload
      for (int i = 0; i < 7; ++i) {
        csvPrinter.printRecord(System.currentTimeMillis(), oneMegaByteString);
      }
    }

    manager.complete();
    s3Client.deleteObject(bucketName, testFile);

    LOGGER.info("Finished verification for multipart upload mode");
  }

  @Override
  public AirbyteMessageConsumer getConsumer(final JsonNode config,
                                            final ConfiguredAirbyteCatalog configuredCatalog,
                                            final Consumer<AirbyteMessage> outputRecordCollector) {
    final S3WriterFactory formatterFactory = new ProductionWriterFactory();
    return new S3Consumer(S3DestinationConfig.getS3DestinationConfig(config), configuredCatalog, formatterFactory, outputRecordCollector);
  }

  /**
   * Note that this method completely ignores s3Config.getBucketPath(), in favor of the bucketPath
   * parameter.
   */
  public static void attemptS3WriteAndDelete(final S3DestinationConfig s3Config, final String bucketPath) {
    attemptS3WriteAndDelete(s3Config, bucketPath, s3Config.getS3Client());
  }

  @VisibleForTesting
  static void attemptS3WriteAndDelete(final S3DestinationConfig s3Config, final String bucketPath, final AmazonS3 s3) {
    final var prefix = bucketPath.isEmpty() ? "" : bucketPath + (bucketPath.endsWith("/") ? "" : "/");
    final String outputTableName = prefix + "_airbyte_connection_test_" + UUID.randomUUID().toString().replaceAll("-", "");
    attemptWriteAndDeleteS3Object(s3Config, outputTableName, s3);
  }

  private static void attemptWriteAndDeleteS3Object(final S3DestinationConfig s3Config, final String outputTableName, final AmazonS3 s3) {
    final var s3Bucket = s3Config.getBucketName();

    s3.putObject(s3Bucket, outputTableName, "check-content");
    s3.deleteObject(s3Bucket, outputTableName);
  }

}
