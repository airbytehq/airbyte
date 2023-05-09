/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.integrations.base.Destination;
import io.airbyte.integrations.destination.record_buffer.FileBuffer;
import io.airbyte.integrations.destination.snowflake.SnowflakeDestination.DestinationType;
import java.util.Map;

public class SnowflakeDestinationResolver {

  public static DestinationType getTypeFromConfig(final JsonNode config) {
    if (isS3Copy(config)) {
      return DestinationType.COPY_S3;
    } else if (isGcsCopy(config)) {
      return DestinationType.COPY_GCS;
    } else {
      return DestinationType.INTERNAL_STAGING;
    }
  }

  public static boolean isS3Copy(final JsonNode config) {
    return config.has("loading_method") && config.get("loading_method").isObject() && config.get("loading_method").has("s3_bucket_name");
  }

  public static boolean isGcsCopy(final JsonNode config) {
    return config.has("loading_method") && config.get("loading_method").isObject() && config.get("loading_method").has("project_id");
  }

  public static int getNumberOfFileBuffers(final JsonNode config) {
    int numOfFileBuffers = FileBuffer.DEFAULT_MAX_CONCURRENT_STREAM_IN_BUFFER;
    if (config.has(FileBuffer.FILE_BUFFER_COUNT_KEY)) {
      numOfFileBuffers = Math.min(config.get(FileBuffer.FILE_BUFFER_COUNT_KEY).asInt(), FileBuffer.MAX_CONCURRENT_STREAM_IN_BUFFER);
    }
    // Only allows for values 10 <= numOfFileBuffers <= 50
    return Math.max(numOfFileBuffers, FileBuffer.DEFAULT_MAX_CONCURRENT_STREAM_IN_BUFFER);
  }

  public static Map<DestinationType, Destination> getTypeToDestination(
                                                                       final String airbyteEnvironment) {
    final SnowflakeS3StagingDestination s3StagingDestination = new SnowflakeS3StagingDestination(airbyteEnvironment);
    final SnowflakeGcsStagingDestination gcsStagingDestination = new SnowflakeGcsStagingDestination(airbyteEnvironment);
    final SnowflakeInternalStagingDestination internalStagingDestination = new SnowflakeInternalStagingDestination(airbyteEnvironment);

    return ImmutableMap.of(
        DestinationType.COPY_S3, s3StagingDestination,
        DestinationType.COPY_GCS, gcsStagingDestination,
        DestinationType.INTERNAL_STAGING, internalStagingDestination);
  }

}
