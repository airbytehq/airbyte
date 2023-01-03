/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
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
  public static final String CONFIGS_INITIAL_SCHEMA_PATH = "configs_database/schema.sql";

  public static final String CONFIGS_SCHEMA_DUMP_PATH = "src/main/resources/configs_database/schema_dump.txt";

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
  public static final String JOBS_INITIAL_SCHEMA_PATH = "jobs_database/schema.sql";

  public static final String JOBS_SCHEMA_DUMP_PATH = "src/main/resources/jobs_database/schema_dump.txt";

  /**
   * Default database connection timeout in milliseconds.
   */
  public static final long DEFAULT_CONNECTION_TIMEOUT_MS = 30 * 1000;

  /**
   * Default amount of time to wait to assert that a database has been migrated, in milliseconds.
   */
  public static final long DEFAULT_ASSERT_DATABASE_TIMEOUT_MS = 2 * DEFAULT_CONNECTION_TIMEOUT_MS;

  /**
   * Private constructor to prevent instantiation.
   */
  private DatabaseConstants() {}

}
