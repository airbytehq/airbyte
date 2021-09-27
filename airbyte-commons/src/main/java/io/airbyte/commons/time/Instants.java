/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.time;

public class Instants {

  public static long toSeconds(long millis) {
    return millis / 1000;
  }

}
