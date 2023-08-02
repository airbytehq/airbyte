/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.integrations.base.SerializedAirbyteMessageConsumer;
import io.airbyte.integrations.destination.jdbc.copy.SwitchingDestination;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;

import java.util.Collections;
import java.util.List;
import java.util.Optional;
import java.util.Set;
import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.function.Consumer;
import lombok.extern.slf4j.Slf4j;

@Slf4j
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
  public SerializedAirbyteMessageConsumer getSerializedMessageConsumer(final JsonNode config,
                                                                       final ConfiguredAirbyteCatalog catalog,
                                                                       final Consumer<AirbyteMessage> outputRecordCollector)
      throws Exception {
    log.info("destination class: {}", getClass());
    final var useAsyncSnowflake = useAsyncSnowflake(config);
    log.info("using async snowflake: {}", useAsyncSnowflake);
    if (useAsyncSnowflake) {
      return new SnowflakeInternalStagingDestination(airbyteEnvironment).getSerializedMessageConsumer(config, catalog, outputRecordCollector);
    } else {
      return new ShimToSerializedAirbyteMessageConsumer(getConsumer(config, catalog, outputRecordCollector));
    }

  }

  public static boolean useAsyncSnowflake(final JsonNode config) {
    final Set<String> stagingLoadingMethods = Set.of("internal staging", "internal-staging", "internal_staging");

    return Optional.of(config)
            .map(node -> node.get("loading_method"))
            .map(node -> node.get("method"))
            .map(JsonNode::asText)
            .map(String::toLowerCase)
            .map(loadingMethod -> stagingLoadingMethods.contains(loadingMethod))
            .orElse(false);
  }

}
