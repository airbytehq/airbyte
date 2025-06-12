/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.test.fixtures.legacy

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus
import io.airbyte.protocol.models.v0.ConnectorSpecification

interface Integration {
    /**
     * Fetch the specification for the integration.
     *
     * @return specification.
     * @throws Exception
     * - any exception.
     */
    @Throws(Exception::class) fun spec(): ConnectorSpecification

    /**
     * Check whether, given the current configuration, the integration can connect to the
     * integration.
     *
     * @param config
     * - integration-specific configuration object as json. e.g. { "username": "airbyte",
     * "password": "super secure" }
     * @return Whether or not the connection was successful. Optional message if it was not.
     * @throws Exception
     * - any exception.
     */
    @Throws(Exception::class) fun check(config: JsonNode): AirbyteConnectionStatus?
}
