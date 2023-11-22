/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.destination_async;

import static org.junit.jupiter.api.Assertions.assertEquals;

import org.junit.jupiter.api.Test;

public class GlobalMemoryManagerTest {

  private static final long BYTES_MB = 1024 * 1024;

  @Test
  void test() {
    final GlobalMemoryManager mgr = new GlobalMemoryManager(15 * BYTES_MB);

    assertEquals(10 * BYTES_MB, mgr.requestMemory());
    assertEquals(5 * BYTES_MB, mgr.requestMemory());
    assertEquals(0, mgr.requestMemory());

    mgr.free(10 * BYTES_MB);
    assertEquals(10 * BYTES_MB, mgr.requestMemory());
    mgr.free(16 * BYTES_MB);
    assertEquals(10 * BYTES_MB, mgr.requestMemory());
  }

}
