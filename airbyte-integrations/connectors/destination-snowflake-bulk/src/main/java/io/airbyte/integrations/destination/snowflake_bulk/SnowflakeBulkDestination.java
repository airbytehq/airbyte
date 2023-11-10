/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake_bulk;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.cdk.integrations.base.AirbyteMessageConsumer;
import io.airbyte.cdk.integrations.base.Destination;
import io.airbyte.cdk.integrations.base.SerializedAirbyteMessageConsumer;
import io.airbyte.cdk.integrations.base.adaptive.AdaptiveDestinationRunner;
import io.airbyte.integrations.destination.snowflake.SnowflakeInternalStagingDestination;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import java.util.function.Consumer;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class SnowflakeBulkDestination extends SnowflakeInternalStagingDestination implements Destination {
  private static final Logger LOGGER = LoggerFactory.getLogger(SnowflakeBulkDestination.class);

  public SnowflakeBulkDestination(final String airbyteEnvironment) {
    super(airbyteEnvironment);
  }

  @Override
  public SerializedAirbyteMessageConsumer getSerializedMessageConsumer(final JsonNode config,
      final ConfiguredAirbyteCatalog catalog, final Consumer<AirbyteMessage> outputRecordCollector) {
    return new ShimToSerializedAirbyteMessageConsumer(getConsumer(config, catalog, outputRecordCollector));
  }

  @Override
  public AirbyteMessageConsumer getConsumer(final JsonNode config,
      final ConfiguredAirbyteCatalog catalog,
      final Consumer<AirbyteMessage> outputRecordCollector) {
    return new BulkConsumer(outputRecordCollector, this.getDatabase(this.getDataSource(config)), getSqlOperations(), getNamingResolver(), config, catalog);
  }


  public static final String AIRBYTE_OSS = "airbyte_oss";
  public static final String AIRBYTE_CLOUD = "airbyte_cloud";
  public static void main(final String[] args) throws Exception {
    LOGGER.info("starting destination: {}", SnowflakeBulkDestination.class);
    AdaptiveDestinationRunner.baseOnEnv()
        .withOssDestination(() -> new SnowflakeBulkDestination(AIRBYTE_OSS))
        .withCloudDestination(() -> new SnowflakeBulkDestination(AIRBYTE_CLOUD))
        .run(args);

    LOGGER.info("completed destination: {}", SnowflakeBulkDestination.class);
  }
}
