/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.logging;

import com.google.common.annotations.VisibleForTesting;

public class LoggingHelper {

  public enum Color {

    BLACK("\u001b[30m"),
    RED("\u001b[31m"),
    GREEN("\u001b[32m"),
    YELLOW("\u001b[33m"),
    BLUE("\u001b[34m"),
    MAGENTA("\u001b[35m"),
    CYAN("\u001b[36m"),
    WHITE("\u001b[37m");

    private final String ansi;

    Color(final String ansiCode) {
      this.ansi = ansiCode;
    }

    public String getCode() {
      return ansi;
    }

  }

  public static final String LOG_SOURCE_MDC_KEY = "log_source";

  @VisibleForTesting
  public static final String RESET = "\u001B[0m";

  public static String applyColor(final Color color, final String msg) {
    return color.getCode() + msg + RESET;
  }

}
