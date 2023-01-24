/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.server.scheduler;

import io.airbyte.commons.temporal.TemporalClient;
import io.airbyte.commons.temporal.TemporalClient.ManualOperationResult;
import io.airbyte.protocol.models.StreamDescriptor;
import java.util.List;
import java.util.Set;
import java.util.UUID;
import lombok.AllArgsConstructor;

@AllArgsConstructor
public class TemporalEventRunner implements EventRunner {

  private final TemporalClient temporalClient;

  @Override
  public void createConnectionManagerWorkflow(final UUID connectionId) {
    temporalClient.submitConnectionUpdaterAsync(connectionId);
  }

  @Override
  public ManualOperationResult startNewManualSync(final UUID connectionId) {
    return temporalClient.startNewManualSync(connectionId);
  }

  @Override
  public ManualOperationResult startNewCancellation(final UUID connectionId) {
    return temporalClient.startNewCancellation(connectionId);
  }

  @Override
  public ManualOperationResult resetConnection(final UUID connectionId,
                                               final List<StreamDescriptor> streamsToReset,
                                               final boolean runSyncImmediately) {
    return temporalClient.resetConnection(connectionId, streamsToReset, runSyncImmediately);
  }

  @Override
  public void forceDeleteConnection(final UUID connectionId) {
    temporalClient.forceDeleteWorkflow(connectionId);
  }

  @Override
  public void migrateSyncIfNeeded(final Set<UUID> connectionIds) {
    temporalClient.migrateSyncIfNeeded(connectionIds);
  }

  @Override
  public void update(final UUID connectionId) {
    temporalClient.update(connectionId);
  }

}
