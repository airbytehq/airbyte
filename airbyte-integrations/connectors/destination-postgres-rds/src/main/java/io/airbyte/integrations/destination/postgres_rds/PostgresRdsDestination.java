/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.postgres_rds;

import io.airbyte.integrations.base.Destination;
import io.airbyte.integrations.base.IntegrationRunner;
import io.airbyte.integrations.destination.postgres.PostgresDestination;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class PostgresRdsDestination {

  private static final Logger LOGGER = LoggerFactory.getLogger(PostgresRdsDestination.class);

  public static void main(final String[] args) throws Exception {
    final Destination destination = PostgresDestination.sshWrappedDestination();
    LOGGER.info("starting destination: Postgres RDS for {}", PostgresRdsDestination.class);
    new IntegrationRunner(destination).run(args);
    LOGGER.info("completed destination: Postgres RDS for {}", PostgresRdsDestination.class);
  }

}
