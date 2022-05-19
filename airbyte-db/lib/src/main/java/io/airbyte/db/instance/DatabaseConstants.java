/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.instance;

import io.airbyte.db.instance.jobs.JobsDatabaseSchema;
import java.util.Collections;
import java.util.Set;

/**
 * Collection of database related constants.
 */
public final class DatabaseConstants {

  /**
   * Logical name of the Configurations database.
   */
  public static final String CONFIGS_DATABASE_LOGGING_NAME = "airbyte configs";

  /**
   * Collection of tables expected to be present in the Configurations database after creation.
   */
  public static final Set<String> CONFIGS_INITIAL_EXPECTED_TABLES = Collections.singleton("airbyte_configs");

  /**
   * Path to the script that contains the initial schema definition for the Configurations database.
   */
  public static final String CONFIGS_SCHEMA_PATH = "configs_database/schema.sql";

  /**
   * Logical name of the Jobs database.
   */
  public static final String JOBS_DATABASE_LOGGING_NAME = "airbyte jobs";

  /**
   * Collection of tables expected to be present in the Jobs database after creation.
   */
  public static final Set<String> JOBS_INITIAL_EXPECTED_TABLES = JobsDatabaseSchema.getTableNames();

  /**
   * Path to the script that contains the initial schema definition for the Jobs database.
   */
  public static final String JOBS_SCHEMA_PATH = "jobs_database/schema.sql";

  /**
   * Private constructor to prevent instantiation.
   */
  private DatabaseConstants() {}

}
