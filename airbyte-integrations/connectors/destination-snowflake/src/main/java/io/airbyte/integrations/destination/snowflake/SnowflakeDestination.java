/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.cdk.integrations.base.AirbyteExceptionHandler;
import io.airbyte.cdk.integrations.base.SerializedAirbyteMessageConsumer;
import io.airbyte.cdk.integrations.destination.jdbc.copy.SwitchingDestination;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.function.Consumer;
import lombok.extern.slf4j.Slf4j;

// TODO: Remove the Switching Destination from this class as part of code cleanup.
@Slf4j
public class SnowflakeDestination extends SwitchingDestination<SnowflakeDestination.DestinationType> {

  public static final ScheduledExecutorService SCHEDULED_EXECUTOR_SERVICE = Executors.newScheduledThreadPool(1);
  private final String airbyteEnvironment;

  enum DestinationType {
    INTERNAL_STAGING
  }

  public SnowflakeDestination(final String airbyteEnvironment) {
    super(DestinationType.class, SnowflakeDestinationResolver::getTypeFromConfig,
        SnowflakeDestinationResolver.getTypeToDestination(airbyteEnvironment));
    this.airbyteEnvironment = airbyteEnvironment;
  }

  @Override
  public SerializedAirbyteMessageConsumer getSerializedMessageConsumer(final JsonNode config,
                                                                       final ConfiguredAirbyteCatalog catalog,
                                                                       final Consumer<AirbyteMessage> outputRecordCollector) {
    AirbyteExceptionHandler.addAllStringsInConfigForDeinterpolation(config);
    return new SnowflakeInternalStagingDestination(airbyteEnvironment).getSerializedMessageConsumer(config, catalog, outputRecordCollector);
  }

  @Override
  public boolean isV2Destination() {
    return true;
  }

}
