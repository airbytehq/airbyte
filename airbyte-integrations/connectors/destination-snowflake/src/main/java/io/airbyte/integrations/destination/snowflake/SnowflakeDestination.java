/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.integrations.base.Destination;
import io.airbyte.integrations.base.IntegrationRunner;
import io.airbyte.integrations.destination.jdbc.copy.SwitchingDestination;
import java.util.Map;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class SnowflakeDestination extends SwitchingDestination<SnowflakeDestination.DestinationType> {

  private static final Logger LOGGER = LoggerFactory.getLogger(SnowflakeDestination.class);

  enum DestinationType {
    INSERT,
    COPY_S3,
    COPY_GCS
  }

  public SnowflakeDestination() {
    super(DestinationType.class, SnowflakeDestination::getTypeFromConfig, getTypeToDestination());
  }

  public static DestinationType getTypeFromConfig(JsonNode config) {
    if (isS3Copy(config)) {
      return DestinationType.COPY_S3;
    } else if (isGcsCopy(config)) {
      return DestinationType.COPY_GCS;
    } else {
      return DestinationType.INSERT;
    }
  }

  public static boolean isS3Copy(JsonNode config) {
    return config.has("loading_method") && config.get("loading_method").isObject() && config.get("loading_method").has("s3_bucket_name");
  }

  public static boolean isGcsCopy(JsonNode config) {
    return config.has("loading_method") && config.get("loading_method").isObject() && config.get("loading_method").has("project_id");
  }

  public static Map<DestinationType, Destination> getTypeToDestination() {
    final SnowflakeInsertDestination insertDestination = new SnowflakeInsertDestination();
    final SnowflakeCopyS3Destination copyS3Destination = new SnowflakeCopyS3Destination();
    final SnowflakeCopyGcsDestination copyGcsDestination = new SnowflakeCopyGcsDestination();

    return ImmutableMap.of(
        DestinationType.INSERT, insertDestination,
        DestinationType.COPY_S3, copyS3Destination,
        DestinationType.COPY_GCS, copyGcsDestination);
  }

  public static void main(String[] args) throws Exception {
    final Destination destination = new SnowflakeDestination();
    LOGGER.info("starting destination: {}", SnowflakeDestination.class);
    new IntegrationRunner(destination).run(args);
    LOGGER.info("completed destination: {}", SnowflakeDestination.class);
  }

}
