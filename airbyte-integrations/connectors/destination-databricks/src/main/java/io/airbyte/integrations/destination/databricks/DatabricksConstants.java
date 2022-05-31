/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.databricks;

import io.airbyte.db.factory.DatabaseDriver;
import java.util.Set;

public class DatabricksConstants {

  public static final String DATABRICKS_USERNAME = "token";
  public static final String DATABRICKS_DRIVER_CLASS = DatabaseDriver.DATABRICKS.getDriverClassName();

  public static final Set<String> DEFAULT_TBL_PROPERTIES = Set.of(
      "delta.autoOptimize.optimizeWrite = true",
      "delta.autoOptimize.autoCompact = true");

  private DatabricksConstants() {}

}
