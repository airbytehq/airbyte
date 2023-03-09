/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3;

import alex.mojaki.s3upload.MultiPartOutputStream;
import alex.mojaki.s3upload.StreamTransferManager;
import com.amazonaws.services.s3.AmazonS3;
import com.amazonaws.services.s3.model.ListObjectsRequest;
import com.google.common.annotations.VisibleForTesting;
import com.google.common.base.Strings;
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
    final var prefix = bucketPath.endsWith("/") ? bucketPath : bucketPath + "/";
    final String testFile = prefix + "test_" + System.currentTimeMillis();
    try {
      s3Client.putObject(bucketName, testFile, "this is a test file");
    } finally {
      s3Client.deleteObject(bucketName, testFile);
    }
    LOGGER.info("Finished checking for normal upload mode");
  }

  public static void testMultipartUpload(final AmazonS3 s3Client, final String bucketName, final String bucketPath) throws IOException {
    LOGGER.info("Started testing if all required credentials assigned to user for multipart upload");
    final var prefix = bucketPath.endsWith("/") ? bucketPath : bucketPath + "/";
    final String testFile = prefix + "test_" + System.currentTimeMillis();
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
  public static boolean testCustomEndpointSecured(final String endpoint) {
    // if user does not use a custom endpoint, do not fail
    if (endpoint == null || endpoint.length() == 0) {
      return true;
    } else {
      return endpoint.startsWith("https://");
    }
  }

  @VisibleForTesting
  static void attemptS3WriteAndDelete(final S3StorageOperations storageOperations,
                                      final S3DestinationConfig s3Config,
                                      final String bucketPath,
                                      final AmazonS3 s3) {
    final String prefix;
    if (Strings.isNullOrEmpty(bucketPath)) {
      prefix = "";
    } else if (bucketPath.endsWith("/")) {
      prefix = bucketPath;
    } else {
      prefix = bucketPath + "/";
    }

    final String outputTableName = prefix + "_airbyte_connection_test_" + UUID.randomUUID().toString().replaceAll("-", "");
    attemptWriteAndDeleteS3Object(storageOperations, s3Config, outputTableName, s3);
  }

  /**
   * Runs some permissions checks: 1. Check whether the bucket exists; create it if not 2. Check
   * whether s3://bucketName/bucketPath/ exists; create it (with empty contents) if not. (if
   * bucketPath is null/empty-string, then skip this step) 3. Attempt to create and delete
   * s3://bucketName/outputTableName 4. Attempt to list all objects in the bucket
   */
  private static void attemptWriteAndDeleteS3Object(final S3StorageOperations storageOperations,
                                                    final S3DestinationConfig s3Config,
                                                    final String outputTableName,
                                                    final AmazonS3 s3) {
    final var s3Bucket = s3Config.getBucketName();
    final var bucketPath = s3Config.getBucketPath();

    if (!Strings.isNullOrEmpty(bucketPath)) {
      storageOperations.createBucketIfNotExists();
    }
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
