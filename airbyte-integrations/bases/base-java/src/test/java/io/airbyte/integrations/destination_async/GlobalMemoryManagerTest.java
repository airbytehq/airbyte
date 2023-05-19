/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination_async;

import static org.junit.jupiter.api.Assertions.assertEquals;

import org.junit.jupiter.api.Test;

public class GlobalMemoryManagerTest {

  private static final long BYTES_10_MB = 10 * 1024 * 1024;
  private static final long BYTES_35_MB = 35 * 1024 * 1024;
  private static final long BYTES_5_MB = 5 * 1024 * 1024;

  @Test
  void test() {
    final GlobalMemoryManager mgr = new GlobalMemoryManager(BYTES_35_MB);

    assertEquals(BYTES_10_MB, mgr.requestMemory());
    assertEquals(BYTES_10_MB, mgr.requestMemory());
    assertEquals(BYTES_10_MB, mgr.requestMemory());
    assertEquals(BYTES_5_MB, mgr.requestMemory());
    assertEquals(0, mgr.requestMemory());

    mgr.free(BYTES_10_MB);

    assertEquals(BYTES_10_MB, mgr.requestMemory());
  }

}
