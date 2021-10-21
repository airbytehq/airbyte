/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.logging;

import io.airbyte.commons.application.Application;
import java.util.HashMap;
import java.util.Map;

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

    private final String ainsiCode;

    Color(final String ainsiCode) {
      this.ainsiCode = ainsiCode;
    }

    public String getCode() {
      return ainsiCode;
    }

  }

  public static final String LOG_SOURCE_MDC_KEY = "log_source";

  private static final String RESET = "\u001B[0m";

  public static String applyColor(final Color color, final String msg) {
    return color.getCode() + msg + RESET;
  }

  public static Map<String, String> getExtraMDCEntries(final Application application) {
    return new HashMap<>() {{
      put(LoggingHelper.LOG_SOURCE_MDC_KEY, LoggingHelper.applyColor(Color.GREEN, application.getApplicationName()));
    }};
  }
}
