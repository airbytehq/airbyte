/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake_bulk;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.cdk.integrations.BaseConnector;
import io.airbyte.cdk.integrations.base.AirbyteMessageConsumer;
import io.airbyte.cdk.integrations.base.Destination;
import io.airbyte.cdk.integrations.base.IntegrationRunner;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus.Status;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import java.util.function.Consumer;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class SnowflakeBulkDestination extends BaseConnector implements Destination {
  private static final Logger LOGGER = LoggerFactory.getLogger(SnowflakeBulkDestination.class);

  @Override
  public AirbyteConnectionStatus check(final JsonNode config) {
    return new AirbyteConnectionStatus().withStatus(Status.SUCCEEDED);
  }

  @Override
  public AirbyteMessageConsumer getConsumer(final JsonNode config,
      final ConfiguredAirbyteCatalog catalog,
      final Consumer<AirbyteMessage> outputRecordCollector) {
    return new BulkConsumer(config, catalog, outputRecordCollector);
  }

  public static void main(final String[] args) throws Exception {
    final Destination destination = new SnowflakeBulkDestination();
    LOGGER.info("starting destination: {}", SnowflakeBulkDestination.class);
    new IntegrationRunner(destination).run(args);
    LOGGER.info("completed destination: {}", SnowflakeBulkDestination.class);
  }

}
