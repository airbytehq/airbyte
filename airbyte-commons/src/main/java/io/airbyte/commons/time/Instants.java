/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.time;

public class Instants {

  public static long toSeconds(final long millis) {
    return millis / 1000;
  }

}
