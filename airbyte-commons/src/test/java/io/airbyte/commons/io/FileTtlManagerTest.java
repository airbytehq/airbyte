/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.io;

import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.concurrent.TimeUnit;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class FileTtlManagerTest {

  private Path file1;
  private Path file2;
  private Path file3;

  @BeforeEach

  void setup() throws IOException {
    final Path testRoot = Files.createTempDirectory(Path.of("/tmp"), "ttl_test");
    file1 = Files.createFile(testRoot.resolve("file1"));
    file2 = Files.createFile(testRoot.resolve("file2"));
    file3 = Files.createFile(testRoot.resolve("file3"));
  }

  @Test
  void testExpiresAfterTime() throws InterruptedException {
    final FileTtlManager fileTtlManager = new FileTtlManager(1, TimeUnit.SECONDS, 10);

    assertTrue(Files.exists(file1));
    fileTtlManager.register(file1);
    fileTtlManager.register(file2);
    assertTrue(Files.exists(file1));
    Thread.sleep(10001L);
    fileTtlManager.register(file3);
    assertFalse(Files.exists(file1));
  }

  @Test
  void testExpiresAfterSizeLimit() {
    final FileTtlManager fileTtlManager = new FileTtlManager(1, TimeUnit.HOURS, 2);

    assertTrue(Files.exists(file1));
    fileTtlManager.register(file1);
    assertTrue(Files.exists(file1));
    fileTtlManager.register(file2);
    assertTrue(Files.exists(file1));
    fileTtlManager.register(file3);
    assertFalse(Files.exists(file1));
  }

}
