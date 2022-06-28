/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake;

import io.airbyte.integrations.base.Destination;
import io.airbyte.integrations.base.IntegrationRunner;
import io.airbyte.integrations.destination.jdbc.copy.SwitchingDestination;
import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;

public class SnowflakeDestination extends SwitchingDestination<SnowflakeDestination.DestinationType> {

  public static final ScheduledExecutorService SCHEDULED_EXECUTOR_SERVICE = Executors.newScheduledThreadPool(1);

  enum DestinationType {
    COPY_S3,
    COPY_GCS,
    COPY_AZURE_BLOB,
    INTERNAL_STAGING
  }

  public SnowflakeDestination() {
    super(DestinationType.class, SnowflakeDestinationResolver::getTypeFromConfig, SnowflakeDestinationResolver.getTypeToDestination());
  }

  public static void main(final String[] args) throws Exception {
    final Destination destination = new SnowflakeDestination();
    new IntegrationRunner(destination).run(args);
    SCHEDULED_EXECUTOR_SERVICE.shutdownNow();
  }

}
