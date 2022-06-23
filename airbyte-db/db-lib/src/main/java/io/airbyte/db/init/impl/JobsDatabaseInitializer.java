/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.init.impl;

import io.airbyte.db.check.DatabaseAvailabilityCheck;
import io.airbyte.db.check.impl.JobsDatabaseAvailabilityCheck;
import io.airbyte.db.init.DatabaseInitializer;
import io.airbyte.db.instance.DatabaseConstants;
import java.util.Collection;
import java.util.Optional;
import org.jooq.DSLContext;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Implementation of the {@link DatabaseInitializer} for the Jobs database that creates the schema
 * if it does not currently exist.
 */
public class JobsDatabaseInitializer implements DatabaseInitializer {

  private static final Logger LOGGER = LoggerFactory.getLogger(JobsDatabaseInitializer.class);

  // TODO inject via dependency injection framework
  private final JobsDatabaseAvailabilityCheck databaseAvailablityCheck;

  // TODO inject via dependency injection framework
  private final DSLContext dslContext;

  // TODO inject via dependency injection framework
  private final String initialSchema;

  public JobsDatabaseInitializer(final JobsDatabaseAvailabilityCheck databaseAvailablityCheck,
                                 final DSLContext dslContext,
                                 final String initialSchema) {
    this.databaseAvailablityCheck = databaseAvailablityCheck;
    this.dslContext = dslContext;
    this.initialSchema = initialSchema;
  }

  @Override
  public Optional<DatabaseAvailabilityCheck> getDatabaseAvailabilityCheck() {
    return Optional.ofNullable(databaseAvailablityCheck);
  }

  @Override
  public String getDatabaseName() {
    return DatabaseConstants.JOBS_DATABASE_LOGGING_NAME;
  }

  @Override
  public Optional<DSLContext> getDslContext() {
    return Optional.ofNullable(dslContext);
  }

  @Override
  public String getInitialSchema() {
    return initialSchema;
  }

  @Override
  public Logger getLogger() {
    return LOGGER;
  }

  @Override
  public Optional<Collection<String>> getTableNames() {
    return Optional.of(DatabaseConstants.JOBS_INITIAL_EXPECTED_TABLES);
  }

}
