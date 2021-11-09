/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.bytes;

public class ByteUtils {

  public static long getSizeInBytes(String s) {
    return s.length() * 2; // by default UTF-8 encoding takes 2bytes per char
  }

}
