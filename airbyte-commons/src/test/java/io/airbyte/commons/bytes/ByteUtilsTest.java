/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.bytes;

import static org.junit.jupiter.api.Assertions.*;

import java.nio.charset.StandardCharsets;
import org.apache.commons.lang3.RandomStringUtils;
import org.junit.jupiter.api.Test;

class ByteUtilsTest {

  @Test
  public void testIt() {
    for (int i = 1; i < 1000; i++) {
      String s = RandomStringUtils.random(i);
      // for now the formula is just hardcoded to str length * 2
      assertEquals(s.getBytes(StandardCharsets.UTF_8).length, ByteUtils.getSizeInBytesForUTF8CharSet(s), "The bytes length should be equal.");
    }
  }

}
