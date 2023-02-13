/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.check.impl;

import io.airbyte.db.check.DatabaseAvailabilityCheck;
import io.airbyte.db.instance.DatabaseConstants;
import java.util.Optional;
import org.jooq.DSLContext;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Implementation of the {@link DatabaseAvailabilityCheck} for the Jobs database.
 */
public class JobsDatabaseAvailabilityCheck implements DatabaseAvailabilityCheck {

  private static final Logger LOGGER = LoggerFactory.getLogger(JobsDatabaseAvailabilityCheck.class);

  // TODO inject via dependency injection framework
  private final DSLContext dslContext;

  // TODO inject via dependency injection framework
  private final long timeoutMs;

  public JobsDatabaseAvailabilityCheck(final DSLContext dslContext, final long timeoutMs) {
    this.dslContext = dslContext;
    this.timeoutMs = timeoutMs;
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
  public Logger getLogger() {
    return LOGGER;
  }

  @Override
  public long getTimeoutMs() {
    return timeoutMs;
  }

}
