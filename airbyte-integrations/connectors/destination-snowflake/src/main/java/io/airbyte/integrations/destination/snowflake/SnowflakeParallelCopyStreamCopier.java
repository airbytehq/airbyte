/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake;

import java.util.List;
import java.util.StringJoiner;
import java.util.concurrent.ExecutorService;

interface SnowflakeParallelCopyStreamCopier {

  default String generateFilesList(List<String> files) {
    StringJoiner joiner = new StringJoiner(",");
    files.forEach(filename -> joiner.add("'" + filename.substring(filename.lastIndexOf("/") + 1) + "'"));
    return joiner.toString();
  }

  default void copyFilesInParallel(List<List<String>> partitions, ExecutorService executorService) {
    partitions.forEach(files -> {
      try {
        executorService.execute(() -> copyIntoStage(files));
      } catch (Exception e) {
        throw new RuntimeException("Failed to copy files from stage to tmp table {}" + e);
      } finally {
        executorService.shutdown();
      }
    });
  }

  void copyIntoStage(List<String> files);

  String generateBucketPath();

}
