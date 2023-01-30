/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.debezium;

import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.debezium.engine.ChangeEvent;
import java.util.Map;

/**
 * This interface is used to allow connectors to save the offset and schema history in the manner
 * which suits them. Also, it adds some utils to verify CDC event status.
 */
public interface CdcStateHandler {

  AirbyteMessage saveState(Map<String, String> offset, String dbHistory);

  AirbyteMessage saveStateAfterCompletionOfSnapshotOfNewStreams();

  /**
   * This function indicates if the event is part of the snapshot or not.
   *
   * @param event Event from the CDC load
   * @return Returns `true` when the DB event is part of the snapshot load. Otherwise, returns `false`
   */
  boolean isSnapshotEvent(ChangeEvent<String, String> event);

  /**
   * This function checks if the event we are processing in the loop is already behind the offse so
   * the process can safety save the state.
   *
   * @param offset DB CDC offset
   * @param event Event from the CDC load
   * @return Returns `true` when the record is behind the offset. Otherwise, it returns `false`
   */
  boolean isRecordBehindOffset(Map<String, String> offset, ChangeEvent<String, String> event);
}
