/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.base;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.util.AutoCloseableIterator;
import io.airbyte.protocol.models.v0.AirbyteCatalog;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;

public interface Source extends Integration {

  /**
   * Discover the current schema in the source.
   *
   * @param config - integration-specific configuration object as json. e.g. { "username": "airbyte",
   *        "password": "super secure" }
   * @return Description of the schema.
   * @throws Exception - any exception.
   */
  AirbyteCatalog discover(JsonNode config) throws Exception;

  /**
   * Return a iterator of messages pulled from the source.
   *
   * @param config - integration-specific configuration object as json. e.g. { "username": "airbyte",
   *        "password": "super secure" }
   * @param catalog - schema of the incoming messages.
   * @param state - state of the incoming messages.
   * @return {@link AutoCloseableIterator} that produces message. The iterator will be consumed until
   *         no records remain or until an exception is thrown. {@link AutoCloseableIterator#close()}
   *         will always be called once regardless of success or failure.
   * @throws Exception - any exception.
   */
  AutoCloseableIterator<AirbyteMessage> read(JsonNode config, ConfiguredAirbyteCatalog catalog, JsonNode state) throws Exception;

}
