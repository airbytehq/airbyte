/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.instance.toys;

import io.airbyte.db.check.DatabaseAvailabilityCheck;
import java.util.Optional;
import org.jooq.DSLContext;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class ToysDatabaseAvailabilityCheck implements DatabaseAvailabilityCheck {

  private static final Logger LOGGER = LoggerFactory.getLogger(ToysDatabaseAvailabilityCheck.class);

  private final DSLContext dslContext;

  private final long timeoutMs;

  public ToysDatabaseAvailabilityCheck(final DSLContext dslContext, final long timeoutMs) {
    this.dslContext = dslContext;
    this.timeoutMs = timeoutMs;
  }

  @Override
  public String getDatabaseName() {
    return ToysDatabaseConstants.DATABASE_LOGGING_NAME;
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
