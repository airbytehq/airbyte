/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.scheduler.app;

import java.nio.file.Paths;

public class JobLogs {

  public static final String ROOT_PATH = "logs/jobs";

  public static String getLogDirectory(final String scope) {
    return Paths.get(ROOT_PATH, scope).toString();
  }

}
