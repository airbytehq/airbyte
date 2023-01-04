/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.dest_state_lifecycle_manager;

import io.airbyte.protocol.models.v0.AirbyteMessage;
import java.util.Queue;

/**
 * This class manages the lifecycle of state message. It tracks state messages that are in 3 states:
 * <ol>
 * <li>pending - associated records have been accepted by the connector but has NOT been pushed to
 * the destination</li>
 * <li>flushed - associated records have been flushed to tmp storage in the destination but have NOT
 * been committed</li>
 * <li>committed - associated records have been committed</li>
 * </ol>
 *
 * Since the methods for flushing and committing are not atomic, adding in a method
 * `markPendingAsCommitted` while deprecating `
 */
public interface DestStateLifecycleManager {

  /**
   * Accepts a state into the manager. The state starts in a pending state.
   *
   * @param message - airbyte message of type state
   */
  void addState(AirbyteMessage message);

  /**
   * Moves any tracked state messages that are currently pending to flushed.
   *
   * @Deprecated
   */
  void markPendingAsFlushed();

  /**
   * List all tracked state messages that are flushed.
   *
   * @return list of state messages
   */
  Queue<AirbyteMessage> listFlushed();

  /**
   * Moves any tracked state messages that are currently flushed to committed.
   *
   * @Deprecated
   */
  void markFlushedAsCommitted();

  /**
   * Moves any committed state message that are emitted to the platform as emitted. This is to avoid
   * emitting duplicate state messages back to the platform
   */
  void markCommittedAsEmitted();

  /**
   * Moves any tracked state messages that are currently pending to committed.
   *
   * Note: that this is skipping "flushed" state since flushed meant that this was using a staging
   * area to hold onto files, for the changes with checkpointing this step is skipped. It follows
   * under the guiding principle that destination needs to commit
   * {@link io.airbyte.protocol.models.AirbyteRecordMessage} more frequently to checkpoint. The new
   * transaction logic will be:
   *
   * Buffer -(flush)-> Staging (Blob Storage) -(commit to airbyte_raw)-> Destination table
   */
  void markPendingAsCommitted();

  /**
   * List all tracked state messages that are committed.
   *
   * @return list of state messages
   */
  Queue<AirbyteMessage> listCommitted();

}
