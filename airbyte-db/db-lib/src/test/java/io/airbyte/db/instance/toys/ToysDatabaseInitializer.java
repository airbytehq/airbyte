/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.instance.toys;

import io.airbyte.db.check.DatabaseAvailabilityCheck;
import io.airbyte.db.init.DatabaseInitializer;
import java.util.Collection;
import java.util.Optional;
import java.util.Set;
import org.jooq.DSLContext;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class ToysDatabaseInitializer implements DatabaseInitializer {

  private static final Logger LOGGER = LoggerFactory.getLogger(ToysDatabaseInitializer.class);

  private final DatabaseAvailabilityCheck databaseAvailablityCheck;

  private final DSLContext dslContext;

  private final String initialSchema;

  public ToysDatabaseInitializer(final DatabaseAvailabilityCheck databaseAvailablityCheck,
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
    return ToysDatabaseConstants.DATABASE_LOGGING_NAME;
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
    return Optional.of(Set.of(ToysDatabaseConstants.TABLE_NAME));
  }

}
