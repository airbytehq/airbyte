package io.airbyte.integrations.destination.snowflake;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.integrations.base.Destination;
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

  public static Map<DestinationType, Destination> getTypeToDestination() {
    final SnowflakeCopyS3Destination copyS3Destination = new SnowflakeCopyS3Destination();
    final SnowflakeCopyGcsDestination copyGcsDestination = new SnowflakeCopyGcsDestination();
    final SnowflakeInternalStagingDestination internalStagingDestination = new SnowflakeInternalStagingDestination();

    return ImmutableMap.of(
        DestinationType.COPY_S3, copyS3Destination,
        DestinationType.COPY_GCS, copyGcsDestination,
        DestinationType.INTERNAL_STAGING, internalStagingDestination);
  }
}
