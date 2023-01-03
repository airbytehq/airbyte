/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake;

import java.util.List;
import java.util.StringJoiner;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.stream.Collectors;

interface SnowflakeParallelCopyStreamCopier {

  /**
   * Generates list of staging files. See more
   * https://docs.snowflake.com/en/user-guide/data-load-considerations-load.html#lists-of-files
   */
  default String generateFilesList(List<String> files) {
    StringJoiner joiner = new StringJoiner(",");
    files.forEach(filename -> joiner.add("'" + filename.substring(filename.lastIndexOf("/") + 1) + "'"));
    return joiner.toString();
  }

  /**
   * Executes async copying of staging files.This method should block until the copy/upload has
   * completed.
   */
  default void copyFilesInParallel(List<List<String>> partitions) {
    ExecutorService executorService = Executors.newFixedThreadPool(5);
    List<CompletableFuture<Void>> futures = partitions.stream()
        .map(partition -> CompletableFuture.runAsync(() -> copyIntoStage(partition), executorService))
        .collect(Collectors.toList());

    try {
      // wait until all futures ready
      CompletableFuture.allOf(futures.toArray(new CompletableFuture[0])).join();
    } catch (Exception e) {
      throw new RuntimeException("Failed to copy files from stage to tmp table {}" + e);
    } finally {
      executorService.shutdown();
    }
  }

  /**
   * Copies staging files to the temporary table using <COPY INTO> statement
   */
  void copyIntoStage(List<String> files);

  /**
   * Generates full bucket/container path to staging files
   */
  String generateBucketPath();

}
