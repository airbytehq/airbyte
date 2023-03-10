/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
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
  default boolean isSnapshotEvent(final ChangeEvent<String, String> event) {
    return false;
  }

  /**
   * This function checks if the event we are processing in the loop is already behind the offset so
   * the process can safety save the state.
   *
   * @param offset DB CDC offset
   * @param event Event from the CDC load
   * @return Returns `true` when the record is behind the offset. Otherwise, it returns `false`
   */
  default boolean isRecordBehindOffset(final Map<String, String> offset, final ChangeEvent<String, String> event) {
    return false;
  }

  /**
   * This function compares two offsets to make sure both are not pointing to the same position. The
   * main purpose is to avoid sending same offset multiple times.
   *
   * @param offsetA Offset to compare
   * @param offsetB Offset to compare
   * @return Returns `true` if both offsets are at the same position. Otherwise, it returns `false`
   */
  default boolean isSameOffset(final Map<String, String> offsetA, final Map<String, String> offsetB) {
    return true;
  }

}
