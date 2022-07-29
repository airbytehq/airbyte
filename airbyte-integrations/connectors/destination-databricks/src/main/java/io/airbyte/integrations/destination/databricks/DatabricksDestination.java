/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.databricks;

import io.airbyte.integrations.base.Destination;
import io.airbyte.integrations.base.IntegrationRunner;
import io.airbyte.integrations.destination.jdbc.copy.SwitchingDestination;
import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;

public class DatabricksDestination extends SwitchingDestination<DatabricksStorageType> {

  public static final ScheduledExecutorService SCHEDULED_EXECUTOR_SERVICE = Executors.newScheduledThreadPool(1);

  public DatabricksDestination() {
    super(DatabricksStorageType.class, DatabricksDestinationResolver::getTypeFromConfig, DatabricksDestinationResolver.getTypeToDestination());
  }

  public static void main(final String[] args) throws Exception {
    final Destination destination = new DatabricksDestination();
    new IntegrationRunner(destination).run(args);
    SCHEDULED_EXECUTOR_SERVICE.shutdownNow();
  }

}
