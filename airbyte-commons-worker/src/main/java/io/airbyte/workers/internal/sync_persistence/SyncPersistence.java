/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.internal.sync_persistence;

import io.airbyte.protocol.models.AirbyteStateMessage;

public interface SyncPersistence extends AutoCloseable {

  void persist(final AirbyteStateMessage stateMessage);

}
