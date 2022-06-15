/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.debezium;

import io.airbyte.protocol.models.AirbyteMessage;
import java.util.Map;

/**
 * This interface is used to allow connectors to save the offset and schema history in the manner
 * which suits them
 */
@FunctionalInterface
public interface CdcStateHandler {

  AirbyteMessage saveState(Map<String, String> offset, String dbHistory);

}
