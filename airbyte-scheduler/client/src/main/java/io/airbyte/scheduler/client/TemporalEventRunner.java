/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.scheduler.client;

import io.airbyte.protocol.models.StreamDescriptor;
import io.airbyte.workers.temporal.TemporalClient;
import io.airbyte.workers.temporal.TemporalClient.ManualOperationResult;
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
  public ManualOperationResult resetConnection(final UUID connectionId, final List<StreamDescriptor> streamsToReset) {
    return temporalClient.resetConnection(connectionId, streamsToReset);
  }

  @Override
  public ManualOperationResult synchronousResetConnection(final UUID connectionId, final List<StreamDescriptor> streamsToReset) {
    return temporalClient.synchronousResetConnection(connectionId, streamsToReset);
  }

  @Override
  public void deleteConnection(final UUID connectionId) {
    temporalClient.deleteConnection(connectionId);
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
