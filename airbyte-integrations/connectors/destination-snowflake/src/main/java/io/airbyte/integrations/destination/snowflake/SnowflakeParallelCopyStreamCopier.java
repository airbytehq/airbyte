/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake;

import java.util.ArrayList;
import java.util.List;
import java.util.StringJoiner;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.ExecutorService;
import java.util.stream.IntStream;

interface SnowflakeParallelCopyStreamCopier {

  default String generateFilesList(List<String> files) {
    StringJoiner joiner = new StringJoiner(",");
    files.forEach(filename -> joiner.add("'" + filename.substring(filename.lastIndexOf("/") + 1) + "'"));
    return joiner.toString();
  }

  default void copyFilesInParallel(List<List<String>> partitions, ExecutorService executorService) {

    CompletableFuture[] futures = new CompletableFuture[partitions.size()];
    IntStream.range(0, partitions.size()).forEach(i -> {
      List<String> partition = partitions.get(i);
      futures[i] = CompletableFuture.runAsync(() -> copyIntoStage(partition), executorService);
    });
    try {
        // This will wait until all futures ready.
        CompletableFuture.allOf(futures).join();
      } catch (Exception e) {
        throw new RuntimeException("Failed to copy files from stage to tmp table {}" + e);
      } finally {
        executorService.shutdown();
      }
  }

  void copyIntoStage(List<String> files);

  String generateBucketPath();

}
