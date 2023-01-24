/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.server.scheduler;

import io.airbyte.commons.temporal.TemporalClient.ManualOperationResult;
import io.airbyte.protocol.models.StreamDescriptor;
import java.util.List;
import java.util.Set;
import java.util.UUID;

public interface EventRunner {

  void createConnectionManagerWorkflow(final UUID connectionId);

  ManualOperationResult startNewManualSync(final UUID connectionId);

  ManualOperationResult startNewCancellation(final UUID connectionId);

  ManualOperationResult resetConnection(final UUID connectionId, final List<StreamDescriptor> streamsToReset, final boolean runSyncImmediately);

  void forceDeleteConnection(final UUID connectionId);

  // TODO: Delete
  @Deprecated(forRemoval = true)
  void migrateSyncIfNeeded(final Set<UUID> connectionIds);

  void update(final UUID connectionId);

}
