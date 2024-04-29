/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.cdk.integrations.base.Destination;
import io.airbyte.integrations.destination.snowflake.SnowflakeDestination.DestinationType;
import java.util.Map;

public class SnowflakeDestinationResolver {

  public static DestinationType getTypeFromConfig(final JsonNode config) {
    return DestinationType.INTERNAL_STAGING;
  }

  public static Map<DestinationType, Destination> getTypeToDestination(final String airbyteEnvironment) {
    final SnowflakeInternalStagingDestination internalStagingDestination = new SnowflakeInternalStagingDestination(airbyteEnvironment);

    return ImmutableMap.of(DestinationType.INTERNAL_STAGING, internalStagingDestination);
  }

}
