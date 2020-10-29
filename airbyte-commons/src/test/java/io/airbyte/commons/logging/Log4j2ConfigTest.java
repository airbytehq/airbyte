/*
 * MIT License
 *
 * Copyright (c) 2020 Airbyte
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
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

public class Log4j2ConfigTest {

  private static final Path TEST_ROOT = Path.of("/tmp/airbyte_tests");
  private Path root;

  @BeforeEach
  void setUp() throws IOException {
    root = Files.createTempDirectory(Files.createDirectories(TEST_ROOT), "test");
    MDC.clear();
  }

  @Test
  void testWorkerDispatch() throws InterruptedException {
    final Logger logger = LoggerFactory.getLogger("testWorkerDispatch");

    final String filename = "logs.log";

    ExecutorService executor = Executors.newFixedThreadPool(1);
    executor.submit(() -> {
      MDC.put("context", "worker");
      MDC.put("job_root", root.toString());
      MDC.put("job_log_filename", filename);
      MDC.put("job_id", "1");
      logger.error("random message testWorkerDispatch");
      MDC.clear();
    });

    executor.shutdown();
    executor.awaitTermination(10, TimeUnit.SECONDS);

    assertTrue(IOs.readFile(root, filename).contains("random message testWorkerDispatch"));
  }

  @Test
  void testLogSeparateFiles() throws InterruptedException {
    final Logger logger = LoggerFactory.getLogger("testLogSeparateFiles");

    final String filename = "logs.log";
    final Path root1 = root.resolve("1");
    final Path root2 = root.resolve("2");

    ExecutorService executor = Executors.newFixedThreadPool(2);
    executor.submit(() -> {
      MDC.put("job_root", root1.toString());
      MDC.put("job_log_filename", filename);
      MDC.put("job_id", "1");
      logger.error("random message 1");
    });

    executor.submit(() -> {
      MDC.put("job_root", root2.toString());
      MDC.put("job_log_filename", filename);
      MDC.put("job_id", "2");
      logger.error("random message 2");
    });

    executor.shutdown();
    executor.awaitTermination(10, TimeUnit.SECONDS);

    assertTrue(IOs.readFile(root1, filename).contains("random message 1"));
    assertTrue(IOs.readFile(root2, filename).contains("random message 2"));
  }

  @Test
  void testLogNoJobRoot() throws InterruptedException {
    final Logger logger = LoggerFactory.getLogger("testWorkerDispatch");

    final String filename = "logs.log";

    ExecutorService executor = Executors.newFixedThreadPool(1);
    executor.submit(() -> {
      logger.error("random message testLogNoJobRoot");
      MDC.clear();
    });

    executor.shutdown();
    executor.awaitTermination(10, TimeUnit.SECONDS);

    assertFalse(Files.exists(root.resolve(filename)));
  }

}
