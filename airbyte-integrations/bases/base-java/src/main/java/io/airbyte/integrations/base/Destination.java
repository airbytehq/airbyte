/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.base;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
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

}
