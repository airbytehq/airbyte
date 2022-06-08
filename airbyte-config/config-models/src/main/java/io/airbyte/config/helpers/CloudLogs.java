/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config.helpers;

import io.airbyte.config.storage.DefaultGcsClientFactory;
import io.airbyte.config.storage.DefaultS3ClientFactory;
import io.airbyte.config.storage.MinioS3ClientFactory;
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
@SuppressWarnings("PMD.AvoidThrowingRawExceptionTypes")
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

  static CloudLogs createCloudLogClient(final LogConfigs configs) {
    switch (configs.getStorageConfigs().getType()) {
      case S3 -> {
        return new S3Logs(new DefaultS3ClientFactory(configs.getStorageConfigs().getS3Config()));
      }
      case MINIO -> {
        return new S3Logs(new MinioS3ClientFactory(configs.getStorageConfigs().getMinioConfig()));
      }
      case GCS -> {
        return new GcsLogs(new DefaultGcsClientFactory(configs.getStorageConfigs().getGcsConfig()));
      }
    }

    throw new RuntimeException("Error no cloud credentials configured..");
  }

}
