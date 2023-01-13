/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.debezium;

import io.airbyte.protocol.models.v0.AirbyteMessage;
import java.util.Map;

/**
 * This interface is used to allow connectors to save the offset and schema history in the manner
 * which suits them
 */
public interface CdcStateHandler {

  AirbyteMessage saveState(Map<String, String> offset, String dbHistory);

  AirbyteMessage saveStateAfterCompletionOfSnapshotOfNewStreams();

}
