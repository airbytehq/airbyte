/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.instance;

public interface FlywayConfigurationConstants {

  public static final String BASELINE_VERSION = "0.29.0.001";
  public static final String BASELINE_DESCRIPTION = "Baseline from file-based migration v1";
  public static final Boolean BASELINE_ON_MIGRATION = true;

}
