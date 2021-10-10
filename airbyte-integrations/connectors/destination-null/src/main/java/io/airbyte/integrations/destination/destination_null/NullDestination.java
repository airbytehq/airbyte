/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.destination_null;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.integrations.BaseConnector;
import io.airbyte.integrations.base.AirbyteMessageConsumer;
import io.airbyte.integrations.base.Destination;
import io.airbyte.integrations.base.IntegrationRunner;
import io.airbyte.integrations.destination.destination_null.logger.NullDestinationLogger;
import io.airbyte.integrations.destination.destination_null.logger.NullDestinationLoggerFactory;
import io.airbyte.protocol.models.AirbyteConnectionStatus;
import io.airbyte.protocol.models.AirbyteConnectionStatus.Status;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import java.util.function.Consumer;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class NullDestination extends BaseConnector implements Destination {

  public static void main(String[] args) throws Exception {
    new IntegrationRunner(new NullDestination()).run(args);
  }

  /**
   * The null destination is always available!
   */
  @Override
  public AirbyteConnectionStatus check(JsonNode config) {
    return new AirbyteConnectionStatus().withStatus(Status.SUCCEEDED);
  }

  @Override
  public AirbyteMessageConsumer getConsumer(JsonNode config,
                                            ConfiguredAirbyteCatalog configuredCatalog,
                                            Consumer<AirbyteMessage> outputRecordCollector) {
    return new NullConsumer(new NullDestinationLoggerFactory(config), configuredCatalog, outputRecordCollector);
  }

}
