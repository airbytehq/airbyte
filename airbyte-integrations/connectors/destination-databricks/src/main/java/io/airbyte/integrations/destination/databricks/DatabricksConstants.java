/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.databricks;

import java.util.Set;

public class DatabricksConstants {

  public static final String DATABRICKS_USERNAME = "token";
  public static final String DATABRICKS_DRIVER_CLASS = "com.simba.spark.jdbc.Driver";

  public static final Set<String> DEFAULT_TBL_PROPERTIES = Set.of(
      "delta.autoOptimize.optimizeWrite = true",
      "delta.autoOptimize.autoCompact = true");

}
