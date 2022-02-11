/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.bytes;

import java.nio.charset.StandardCharsets;

public class ByteUtils {

  /**
   * Encodes this String into a sequence of bytes using the given charset. UTF-8 is based on 8-bit
   * code units. Each character is encoded as 1 to 4 bytes. The first 128 Unicode code points are
   * encoded as 1 byte in UTF-8.
   *
   * @param s - string where charset length will be counted
   * @return length of bytes for charset
   */
  public static long getSizeInBytesForUTF8CharSet(String s) {
    return s.getBytes(StandardCharsets.UTF_8).length;
  }

}
