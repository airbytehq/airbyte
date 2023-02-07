/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.base;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus;
import io.airbyte.protocol.models.v0.ConnectorSpecification;

public interface Integration {

  /**
   * Fetch the specification for the integration.
   *
   * @return specification.
   * @throws Exception - any exception.
   */
  ConnectorSpecification spec() throws Exception;

  /**
   * Check whether, given the current configuration, the integration can connect to the integration.
   *
   * @param config - integration-specific configuration object as json. e.g. { "username": "airbyte",
   *        "password": "super secure" }
   * @return Whether or not the connection was successful. Optional message if it was not.
   * @throws Exception - any exception.
   */
  AirbyteConnectionStatus check(JsonNode config) throws Exception;

}
