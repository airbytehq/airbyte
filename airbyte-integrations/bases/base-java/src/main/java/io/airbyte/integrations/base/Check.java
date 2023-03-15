/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.base;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;

/**
 * The Check method of the Airbyte Protocol is used by Airbyte Actors to verify proper connectivity.
 * This can include verifying hosts are reachable, proper authentication, ability to read or write,
 * etc.
 */
@FunctionalInterface
public interface Check {

  AirbyteConnectionStatus check(JsonNode config, ConfiguredAirbyteCatalog catalog) throws Exception;

}
