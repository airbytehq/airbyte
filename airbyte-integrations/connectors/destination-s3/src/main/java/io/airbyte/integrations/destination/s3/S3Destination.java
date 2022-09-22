/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3;

import alex.mojaki.s3upload.MultiPartOutputStream;
import alex.mojaki.s3upload.StreamTransferManager;
import com.amazonaws.services.s3.AmazonS3;
import com.amazonaws.services.s3.model.ListObjectsRequest;
import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.annotations.VisibleForTesting;
import io.airbyte.integrations.BaseConnector;
import io.airbyte.integrations.base.AirbyteMessageConsumer;
import io.airbyte.integrations.base.Destination;
import io.airbyte.integrations.base.IntegrationRunner;
import io.airbyte.integrations.destination.NamingConventionTransformer;
import io.airbyte.integrations.destination.record_buffer.FileBuffer;
import io.airbyte.integrations.destination.s3.util.S3NameTransformer;
import io.airbyte.integrations.destination.s3.util.StreamTransferManagerFactory;
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
  private final S3DestinationConfigFactory configFactory;
  private final NamingConventionTransformer nameTransformer;

  public S3Destination() {
    this(new S3DestinationConfigFactory());
  }

  public S3Destination(final S3DestinationConfigFactory configFactory) {
    this.configFactory = configFactory;
    this.nameTransformer = new S3NameTransformer();
  }

  public static void main(final String[] args) throws Exception {
    new IntegrationRunner(new S3Destination()).run(args);
  }

  @Override
  public AirbyteConnectionStatus check(final JsonNode config) {
    try {
      final S3DestinationConfig destinationConfig = configFactory.getS3DestinationConfig(config);
      final AmazonS3 s3Client = destinationConfig.getS3Client();
      final S3StorageOperations storageOperations = new S3StorageOperations(nameTransformer, s3Client, destinationConfig);

      // Test for writing, list and delete
      S3Destination.attemptS3WriteAndDelete(storageOperations, destinationConfig, destinationConfig.getBucketPath());

      // Test single upload (for small files) permissions
      testSingleUpload(s3Client, destinationConfig.getBucketName(), destinationConfig.getBucketPath());

      // Test multipart upload with stream transfer manager
      testMultipartUpload(s3Client, destinationConfig.getBucketName(), destinationConfig.getBucketPath());

      return new AirbyteConnectionStatus().withStatus(Status.SUCCEEDED);
    } catch (final Exception e) {
      LOGGER.error("Exception attempting to access the S3 bucket: ", e);
      return new AirbyteConnectionStatus()
          .withStatus(AirbyteConnectionStatus.Status.FAILED)
          .withMessage("Could not connect to the S3 bucket with the provided configuration. \n" + e
              .getMessage());
    }
  }

  public static void testSingleUpload(final AmazonS3 s3Client, final String bucketName, final String bucketPath) {
    LOGGER.info("Started testing if all required credentials assigned to user for single file uploading");
    if (bucketPath.endsWith("/")) {
      throw new RuntimeException("Bucket Path should not end with /");
    }
    final String testFile = bucketPath + "/" + "test_" + System.currentTimeMillis();
    try {
      s3Client.putObject(bucketName, testFile, "this is a test file");
    } finally {
      s3Client.deleteObject(bucketName, testFile);
    }
    LOGGER.info("Finished checking for normal upload mode");
  }

  public static void testMultipartUpload(final AmazonS3 s3Client, final String bucketName, final String bucketPath) throws IOException {
    LOGGER.info("Started testing if all required credentials assigned to user for multipart upload");
    if (bucketPath.endsWith("/")) {
      throw new RuntimeException("Bucket Path should not end with /");
    }
    final String testFile = bucketPath + "/" + "test_" + System.currentTimeMillis();
    final StreamTransferManager manager = StreamTransferManagerFactory.create(bucketName, testFile, s3Client).get();
    boolean success = false;
    try (final MultiPartOutputStream outputStream = manager.getMultiPartOutputStreams().get(0);
        final CSVPrinter csvPrinter = new CSVPrinter(new PrintWriter(outputStream, true, StandardCharsets.UTF_8), CSVFormat.DEFAULT)) {
      final String oneMegaByteString = "a".repeat(500_000);
      // write a file larger than the 5 MB, which is the default part size, to make sure it is a multipart
      // upload
      for (int i = 0; i < 7; ++i) {
        csvPrinter.printRecord(System.currentTimeMillis(), oneMegaByteString);
      }
      success = true;
    } finally {
      if (success) {
        manager.complete();
      } else {
        manager.abort();
      }
      s3Client.deleteObject(bucketName, testFile);
    }
    LOGGER.info("Finished verification for multipart upload mode");
  }

  /**
   * Note that this method completely ignores s3Config.getBucketPath(), in favor of the bucketPath
   * parameter.
   */
  public static void attemptS3WriteAndDelete(final S3StorageOperations storageOperations,
                                             final S3DestinationConfig s3Config,
                                             final String bucketPath) {
    attemptS3WriteAndDelete(storageOperations, s3Config, bucketPath, s3Config.getS3Client());
  }

  @VisibleForTesting
  static void attemptS3WriteAndDelete(final S3StorageOperations storageOperations,
                                      final S3DestinationConfig s3Config,
                                      final String bucketPath,
                                      final AmazonS3 s3) {
    final var prefix = bucketPath.isEmpty() ? "" : bucketPath + (bucketPath.endsWith("/") ? "" : "/");
    final String outputTableName = prefix + "_airbyte_connection_test_" + UUID.randomUUID().toString().replaceAll("-", "");
    attemptWriteAndDeleteS3Object(storageOperations, s3Config, outputTableName, s3, bucketPath);
  }

  private static void attemptWriteAndDeleteS3Object(final S3StorageOperations storageOperations,
                                                    final S3DestinationConfig s3Config,
                                                    final String outputTableName,
                                                    final AmazonS3 s3,
                                                    final String bucketPath) {
    final var s3Bucket = s3Config.getBucketName();

    storageOperations.createBucketObjectIfNotExists(bucketPath);
    s3.putObject(s3Bucket, outputTableName, "check-content");
    testIAMUserHasListObjectPermission(s3, s3Bucket);
    s3.deleteObject(s3Bucket, outputTableName);
  }

  public static void testIAMUserHasListObjectPermission(final AmazonS3 s3, final String bucketName) {
    LOGGER.info("Started testing if IAM user can call listObjects on the destination bucket");
    final ListObjectsRequest request = new ListObjectsRequest().withBucketName(bucketName).withMaxKeys(1);
    s3.listObjects(request);
    LOGGER.info("Finished checking for listObjects permission");
  }

  @Override
  public AirbyteMessageConsumer getConsumer(final JsonNode config,
                                            final ConfiguredAirbyteCatalog catalog,
                                            final Consumer<AirbyteMessage> outputRecordCollector) {
    final S3DestinationConfig s3Config = S3DestinationConfig.getS3DestinationConfig(config);
    return new S3ConsumerFactory().create(
        outputRecordCollector,
        new S3StorageOperations(nameTransformer, s3Config.getS3Client(), s3Config),
        nameTransformer,
        SerializedBufferFactory.getCreateFunction(s3Config, FileBuffer::new),
        s3Config,
        catalog);
  }

}
