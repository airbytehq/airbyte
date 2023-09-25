/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.integrations.base.Destination;
import io.airbyte.integrations.destination.snowflake.SnowflakeDestination.DestinationType;
import java.util.Map;

public class SnowflakeDestinationResolver {

  public static DestinationType getTypeFromConfig(final JsonNode config) {
    if (config.has("bulk_load_s3_stages")) {
      // Assume 'bulk load' mode if S3 stages are specified
      return DestinationType.BULK_LOAD_FROM_S3;
    } else {
      return DestinationType.INTERNAL_STAGING;
    }
  }

  public static Map<DestinationType, Destination> getTypeToDestination(final String airbyteEnvironment) {
    final SnowflakeInternalStagingDestination internalStagingDestination = new SnowflakeInternalStagingDestination(airbyteEnvironment);
    final SnowflakeBulkLoadDestination BulkLoadDestination = new SnowflakeBulkLoadDestination(airbyteEnvironment);

    return ImmutableMap.of(
        DestinationType.INTERNAL_STAGING,
        internalStagingDestination,
        DestinationType.BULK_LOAD_FROM_S3,
        BulkLoadDestination);
  }

}
