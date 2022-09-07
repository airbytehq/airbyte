/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.logging;

import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

import io.airbyte.commons.io.IOs;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.slf4j.MDC;

class Log4j2ConfigTest {

  private static final Path TEST_ROOT = Path.of("/tmp/airbyte_tests");
  private static final String LOG_FILENAME = "logs.log";
  private Path root;

  @BeforeEach
  void setUp() throws IOException {
    root = Files.createTempDirectory(Files.createDirectories(TEST_ROOT), "test");
    MDC.clear();
  }

  @Test
  void testWorkerDispatch() throws InterruptedException {
    final Logger logger = LoggerFactory.getLogger("testWorkerDispatch");

    final ExecutorService executor = Executors.newFixedThreadPool(1);
    executor.submit(() -> {
      MDC.put("context", "worker");
      MDC.put("job_log_path", root + "/" + LOG_FILENAME);
      logger.error("random message testWorkerDispatch");
      MDC.clear();
    });

    executor.shutdown();
    executor.awaitTermination(10, TimeUnit.SECONDS);

    assertTrue(IOs.readFile(root, LOG_FILENAME).contains("random message testWorkerDispatch"));
  }

  @Test
  void testLogSeparateFiles() throws InterruptedException {
    final Logger logger = LoggerFactory.getLogger("testLogSeparateFiles");

    final Path root1 = root.resolve("1");
    final Path root2 = root.resolve("2");

    final ExecutorService executor = Executors.newFixedThreadPool(2);
    executor.submit(() -> {
      MDC.put("job_log_path", root1 + "/" + LOG_FILENAME);
      logger.error("random message 1");
    });

    executor.submit(() -> {
      MDC.put("job_log_path", root2 + "/" + LOG_FILENAME);
      logger.error("random message 2");
    });

    executor.shutdown();
    executor.awaitTermination(10, TimeUnit.SECONDS);

    assertTrue(IOs.readFile(root1, LOG_FILENAME).contains("random message 1"));
    assertTrue(IOs.readFile(root2, LOG_FILENAME).contains("random message 2"));
  }

  @Test
  void testLogNoJobRoot() throws InterruptedException {
    final Logger logger = LoggerFactory.getLogger("testWorkerDispatch");

    final ExecutorService executor = Executors.newFixedThreadPool(1);
    executor.submit(() -> {
      logger.error("random message testLogNoJobRoot");
      MDC.clear();
    });

    executor.shutdown();
    executor.awaitTermination(10, TimeUnit.SECONDS);

    assertFalse(Files.exists(root.resolve(LOG_FILENAME)));
  }

  @Test
  void testAppDispatch() throws InterruptedException {
    final Logger logger = LoggerFactory.getLogger("testAppDispatch");

    final ExecutorService executor = Executors.newFixedThreadPool(1);
    executor.submit(() -> {
      MDC.put("workspace_app_root", root.toString());
      logger.error("random message testAppDispatch");
      MDC.clear();
    });

    executor.shutdown();
    executor.awaitTermination(10, TimeUnit.SECONDS);

    assertTrue(IOs.readFile(root, LOG_FILENAME).contains("random message testAppDispatch"));
  }

  @Test
  void testLogNoAppRoot() throws InterruptedException {
    final Logger logger = LoggerFactory.getLogger("testAppDispatch");

    final ExecutorService executor = Executors.newFixedThreadPool(1);
    executor.submit(() -> {
      logger.error("random message testLogNoAppRoot");
      MDC.clear();
    });

    executor.shutdown();
    executor.awaitTermination(10, TimeUnit.SECONDS);

    assertFalse(Files.exists(root.resolve(LOG_FILENAME)));
  }

}
