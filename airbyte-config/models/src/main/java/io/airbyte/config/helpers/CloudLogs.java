/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config.helpers;

import java.io.File;
import java.io.IOException;
import java.util.List;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Interface for various Cloud Storage clients supporting Cloud log retrieval.
 *
 * The underlying assumption 1) each file at the path is part of the entire log file represented by
 * that path 2) log files names start with timestamps, making it possible extract the time the file
 * was written from it's name.
 */
public interface CloudLogs {

  Logger LOGGER = LoggerFactory.getLogger(CloudLogs.class);

  /**
   * Retrieve all objects at the given path in lexicographical order, and return their contents as one
   * file.
   */
  File downloadCloudLog(LogConfigs configs, String logPath) throws IOException;

  /**
   * Assume all the lexicographically ordered objects at the given path form one giant log file,
   * return the last numLines lines.
   */
  List<String> tailCloudLog(LogConfigs configs, String logPath, int numLines) throws IOException;

  void deleteLogs(LogConfigs configs, String logPath);

  /**
   * @return true if no cloud logging configuration is set;
   */
  static boolean hasEmptyConfigs(final LogConfigs configs) {
    return !hasMinioConfiguration(configs) && !hasS3Configuration(configs) && !hasGcpConfiguration(configs);
  }

  static CloudLogs createCloudLogClient(final LogConfigs configs) {
    // check if the configs exists, and pick a client.
    if (hasMinioConfiguration(configs)) {
      LOGGER.info("Creating Minio Log Client");
      return new S3Logs();
    }

    if (hasS3Configuration(configs)) {
      LOGGER.info("Creating AWS Log Client");
      return new S3Logs();
    }

    if (hasGcpConfiguration(configs)) {
      LOGGER.info("Creating GCS Log Client");
      return new GcsLogs();
    }

    throw new RuntimeException("Error no cloud credentials configured..");
  }

  /**
   * Logs are configured to go to a Minio instance if the S3MinioEndpoint configuration specifically
   * is set, along with the other default S3 logging configurations.
   *
   * @param configs contains the environment variables to check
   * @return boolean indicating if logs are configured to be sent to minio
   */
  private static boolean hasMinioConfiguration(final LogConfigs configs) {
    return !configs.getS3LogBucket().isBlank() && !configs.getAwsAccessKey().isBlank()
        && !configs.getAwsSecretAccessKey().isBlank() && !configs.getS3MinioEndpoint().isBlank();
  }

  /**
   * Logs are configured to go to S3 if the S3LogBucketRegion configuration specifically is set, along
   * with the other default S3 logging configurations.
   *
   * @param configs contains the configuration values to check
   * @return boolean indicating if logs are configured to be sent to S3
   */
  private static boolean hasS3Configuration(final LogConfigs configs) {
    return !configs.getAwsAccessKey().isBlank() &&
        !configs.getAwsSecretAccessKey().isBlank() &&
        !configs.getS3LogBucketRegion().isBlank() &&
        !configs.getS3LogBucket().isBlank();
  }

  private static boolean hasGcpConfiguration(final LogConfigs configs) {
    return !configs.getGcpStorageBucket().isBlank() &&
        !configs.getGoogleApplicationCredentials().isBlank();
  }

}
