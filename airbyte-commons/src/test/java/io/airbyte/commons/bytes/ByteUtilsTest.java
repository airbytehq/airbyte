/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.bytes;

import static org.junit.jupiter.api.Assertions.*;

import org.apache.commons.lang3.RandomStringUtils;
import org.junit.jupiter.api.Test;

class ByteUtilsTest {

  @Test
  public void testIt() {
    for (int i = 1; i < 1000; i++) {
      String s = RandomStringUtils.random(i);
      // for now the formula is just hardcoded to str length * 2
      assertEquals(i * 2, ByteUtils.getSizeInBytes(s));
    }
  }

}
