/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination_async;

import static org.junit.jupiter.api.Assertions.assertEquals;

import org.junit.jupiter.api.Test;

public class AirbyteFileUtilsTest {

  @Test
  void testByteCountToDisplaySize() {

    assertEquals("500 bytes", AirbyteFileUtils.byteCountToDisplaySize(500L));
    assertEquals("1.95 KB", AirbyteFileUtils.byteCountToDisplaySize(2000L));
    assertEquals("2.93 MB", AirbyteFileUtils.byteCountToDisplaySize(3072000L));
    assertEquals("2.67 GB", AirbyteFileUtils.byteCountToDisplaySize(2872000000L));
    assertEquals("1.82 TB", AirbyteFileUtils.byteCountToDisplaySize(2000000000000L));
  }

}
