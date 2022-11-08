/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config.helpers;

import com.google.common.annotations.VisibleForTesting;
import com.google.common.collect.Lists;
import io.airbyte.commons.string.Strings;
import io.airbyte.config.storage.CloudStorageConfigs;
import io.airbyte.config.storage.CloudStorageConfigs.S3ApiWorkerStorageConfig;
import io.airbyte.config.storage.CloudStorageConfigs.WorkerStorageType;
import java.io.BufferedReader;
import java.io.ByteArrayInputStream;
import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.List;
import java.util.function.Supplier;
import java.util.stream.Collectors;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import software.amazon.awssdk.services.s3.S3Client;
import software.amazon.awssdk.services.s3.model.Delete;
import software.amazon.awssdk.services.s3.model.DeleteObjectsRequest;
import software.amazon.awssdk.services.s3.model.GetObjectRequest;
import software.amazon.awssdk.services.s3.model.ListObjectsV2Request;
import software.amazon.awssdk.services.s3.model.ObjectIdentifier;

@SuppressWarnings({"PMD.ShortVariable", "PMD.CloseResource", "PMD.AvoidFileStream"})
public class S3Logs implements CloudLogs {

  private static final Logger LOGGER = LoggerFactory.getLogger(S3Logs.class);

  private static S3Client s3;

  private final Supplier<S3Client> s3ClientFactory;

  public S3Logs(final Supplier<S3Client> s3ClientFactory) {
    this.s3ClientFactory = s3ClientFactory;
  }

  @Override
  public File downloadCloudLog(final LogConfigs configs, final String logPath) throws IOException {
    return getFile(configs, logPath, LogClientSingleton.DEFAULT_PAGE_SIZE);
  }

  private static String getBucketName(final CloudStorageConfigs configs) {
    final S3ApiWorkerStorageConfig config;
    if (configs.getType() == WorkerStorageType.S3) {
      config = configs.getS3Config();
    } else if (configs.getType() == WorkerStorageType.MINIO) {
      config = configs.getMinioConfig();
    } else {
      throw new IllegalArgumentException("config must be of type S3 or MINIO");
    }
    return config.getBucketName();
  }

  private File getFile(final LogConfigs configs, final String logPath, final int pageSize) throws IOException {
    return getFile(getOrCreateS3Client(), configs, logPath, pageSize);
  }

  @VisibleForTesting
  static File getFile(final S3Client s3Client, final LogConfigs configs, final String logPath, final int pageSize) throws IOException {
    LOGGER.debug("Retrieving logs from S3 path: {}", logPath);

    final var s3Bucket = getBucketName(configs.getStorageConfigs());
    final var randomName = Strings.addRandomSuffix("logs", "-", 5);
    final var tmpOutputFile = new File("/tmp/" + randomName);
    final var os = new FileOutputStream(tmpOutputFile);

    LOGGER.debug("Start S3 list request.");
    final var listObjReq = ListObjectsV2Request.builder().bucket(s3Bucket)
        .prefix(logPath).maxKeys(pageSize).build();
    LOGGER.debug("Start getting S3 objects.");
    // Objects are returned in lexicographical order.
    for (final var page : s3Client.listObjectsV2Paginator(listObjReq)) {
      for (final var objMetadata : page.contents()) {
        final var getObjReq = GetObjectRequest.builder()
            .key(objMetadata.key())
            .bucket(s3Bucket)
            .build();
        final var data = s3Client.getObjectAsBytes(getObjReq).asByteArray();
        os.write(data);
      }
    }
    os.close();

    LOGGER.debug("Done retrieving S3 logs: {}.", logPath);
    return tmpOutputFile;
  }

  @Override
  public List<String> tailCloudLog(final LogConfigs configs, final String logPath, final int numLines) throws IOException {
    LOGGER.debug("Tailing logs from S3 path: {}", logPath);
    final S3Client s3Client = getOrCreateS3Client();

    final var s3Bucket = getBucketName(configs.getStorageConfigs());
    LOGGER.debug("Start making S3 list request.");
    final List<String> ascendingTimestampKeys = getAscendingObjectKeys(s3Client, logPath, s3Bucket);
    final var descendingTimestampKeys = Lists.reverse(ascendingTimestampKeys);

    final var lines = new ArrayList<String>();
    int linesRead = 0;

    LOGGER.debug("Start getting S3 objects.");
    while (linesRead <= numLines && !descendingTimestampKeys.isEmpty()) {
      final var poppedKey = descendingTimestampKeys.remove(0);
      final List<String> currFileLinesReversed = Lists.reverse(getCurrFile(s3Client, s3Bucket, poppedKey));
      for (final var line : currFileLinesReversed) {
        if (linesRead == numLines) {
          break;
        }
        lines.add(0, line);
        linesRead++;
      }
    }

    LOGGER.debug("Done retrieving S3 logs: {}.", logPath);
    return lines;
  }

  @Override
  public void deleteLogs(final LogConfigs configs, final String logPath) {
    LOGGER.debug("Deleting logs from S3 path: {}", logPath);
    final S3Client s3Client = getOrCreateS3Client();

    final var s3Bucket = getBucketName(configs.getStorageConfigs());
    final var keys = getAscendingObjectKeys(s3Client, logPath, s3Bucket)
        .stream().map(key -> ObjectIdentifier.builder().key(key).build())
        .collect(Collectors.toList());
    final Delete del = Delete.builder()
        .objects(keys)
        .build();
    final DeleteObjectsRequest multiObjectDeleteRequest = DeleteObjectsRequest.builder()
        .bucket(s3Bucket)
        .delete(del)
        .build();

    s3Client.deleteObjects(multiObjectDeleteRequest);
    LOGGER.debug("Multiple objects are deleted!");
  }

  private S3Client getOrCreateS3Client() {
    if (s3 == null) {
      s3 = s3ClientFactory.get();
    }
    return s3;
  }

  private static List<String> getAscendingObjectKeys(final S3Client s3Client, final String logPath, final String s3Bucket) {
    final var listObjReq = ListObjectsV2Request.builder().bucket(s3Bucket).prefix(logPath).build();
    final var ascendingTimestampObjs = new ArrayList<String>();

    // Objects are returned in lexicographical order.
    for (final var page : s3Client.listObjectsV2Paginator(listObjReq)) {
      for (final var objMetadata : page.contents()) {
        ascendingTimestampObjs.add(objMetadata.key());
      }
    }
    return ascendingTimestampObjs;
  }

  private static List<String> getCurrFile(final S3Client s3Client, final String s3Bucket, final String poppedKey) throws IOException {
    final var getObjReq = GetObjectRequest.builder()
        .key(poppedKey)
        .bucket(s3Bucket)
        .build();

    final var data = s3Client.getObjectAsBytes(getObjReq).asByteArray();
    final var is = new ByteArrayInputStream(data);
    final var currentFileLines = new ArrayList<String>();
    try (final var reader = new BufferedReader(new InputStreamReader(is, StandardCharsets.UTF_8))) {
      String temp = reader.readLine();
      while (temp != null) {
        currentFileLines.add(temp);
        temp = reader.readLine();
      }
    }
    return currentFileLines;
  }

}
