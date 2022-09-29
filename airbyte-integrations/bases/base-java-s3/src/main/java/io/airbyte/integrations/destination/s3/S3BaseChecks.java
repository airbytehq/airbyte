/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3;

import alex.mojaki.s3upload.MultiPartOutputStream;
import alex.mojaki.s3upload.StreamTransferManager;
import com.amazonaws.services.s3.AmazonS3;
import com.amazonaws.services.s3.model.ListObjectsRequest;
import com.google.common.annotations.VisibleForTesting;
import io.airbyte.integrations.destination.s3.util.StreamTransferManagerFactory;
import java.io.IOException;
import java.io.PrintWriter;
import java.nio.charset.StandardCharsets;
import java.util.UUID;
import org.apache.commons.csv.CSVFormat;
import org.apache.commons.csv.CSVPrinter;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public final class S3BaseChecks {

  private static final Logger LOGGER = LoggerFactory.getLogger(S3BaseChecks.class);

  private S3BaseChecks() {}

  /**
   * Note that this method completely ignores s3Config.getBucketPath(), in favor of the bucketPath
   * parameter.
   */
  public static void attemptS3WriteAndDelete(final S3StorageOperations storageOperations,
                                             final S3DestinationConfig s3Config,
                                             final String bucketPath) {
    attemptS3WriteAndDelete(storageOperations, s3Config, bucketPath, s3Config.getS3Client());
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
   * Checks that S3 custom endpoint uses a variant that only uses HTTPS
   *
   * @param endpoint URL string representing an accessible S3 bucket
   */
  public static void testCustomEndpointSecured(final String endpoint) {
    if (!endpoint.contains("https://")) {
      throw new RuntimeException(
          "S3 custom endpoint does not ensure HTTPS only connection. Please use S3 Access Points endpoints for a secure connection");
    }
  }

  @VisibleForTesting
  static void attemptS3WriteAndDelete(final S3StorageOperations storageOperations,
                                      final S3DestinationConfig s3Config,
                                      final String bucketPath,
                                      final AmazonS3 s3) {
    final var prefix = bucketPath.isEmpty() ? "" : bucketPath + (bucketPath.endsWith("/") ? "" : "/");
    final String outputTableName = prefix + "_airbyte_connection_test_" + UUID.randomUUID().toString().replaceAll("-", "");
    attemptWriteAndDeleteS3Object(storageOperations, s3Config, outputTableName, s3);
  }

  private static void attemptWriteAndDeleteS3Object(final S3StorageOperations storageOperations,
                                                    final S3DestinationConfig s3Config,
                                                    final String outputTableName,
                                                    final AmazonS3 s3) {
    final var s3Bucket = s3Config.getBucketName();

    storageOperations.createBucketObjectIfNotExists(s3Bucket);
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

}
