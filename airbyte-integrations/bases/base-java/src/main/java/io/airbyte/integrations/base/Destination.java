/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.base;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.base.errors.utils.ConnectorName;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import java.util.function.Consumer;

public interface Destination extends Integration {

  /**
   * Return a consumer that writes messages to the destination.
   *
   * @param config - integration-specific configuration object as json. e.g. { "username": "airbyte",
   *        "password": "super secure" }
   * @param catalog - schema of the incoming messages.
   * @return Consumer that accepts message. The {@link AirbyteMessageConsumer#accept(AirbyteMessage)}
   *         will be called n times where n is the number of messages.
   *         {@link AirbyteMessageConsumer#close()} will always be called once regardless of success
   *         or failure.
   * @throws Exception - any exception.
   */
  AirbyteMessageConsumer getConsumer(JsonNode config,
                                     ConfiguredAirbyteCatalog catalog,
                                     Consumer<AirbyteMessage> outputRecordCollector)
      throws Exception;

  static void defaultOutputRecordCollector(final AirbyteMessage message) {
    System.out.println(Jsons.serialize(message));
  }

  /***
   * This method returns connector name which user for error messages mapping
   *
   * @return ConnectorName for example MYSQL or POSTGRES, will return DEFAULT if error message mapping
   *         is not specified
   */
  default ConnectorName getConnectorName() {
    return ConnectorName.DEFAULT;
  }

}
