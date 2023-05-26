/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.integrations.base.AirbyteMessageConsumer2;
import io.airbyte.integrations.destination.jdbc.copy.SwitchingDestination;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.function.Consumer;

public class SnowflakeDestination extends SwitchingDestination<SnowflakeDestination.DestinationType> {

  public static final ScheduledExecutorService SCHEDULED_EXECUTOR_SERVICE = Executors.newScheduledThreadPool(1);
  private final String airbyteEnvironment;

  enum DestinationType {
    COPY_S3,
    COPY_GCS,
    INTERNAL_STAGING
  }

  public SnowflakeDestination(final String airbyteEnvironment) {
    super(DestinationType.class, SnowflakeDestinationResolver::getTypeFromConfig,
        SnowflakeDestinationResolver.getTypeToDestination(airbyteEnvironment));
    this.airbyteEnvironment = airbyteEnvironment;
  }

  @Override
  public AirbyteMessageConsumer2 getConsumer2(final JsonNode config,
                                              final ConfiguredAirbyteCatalog catalog,
                                              final Consumer<AirbyteMessage> outputRecordCollector)
      throws Exception {
    return new SnowflakeInternalStagingDestination(airbyteEnvironment).getConsumer2(config, catalog, outputRecordCollector);
  }

}
