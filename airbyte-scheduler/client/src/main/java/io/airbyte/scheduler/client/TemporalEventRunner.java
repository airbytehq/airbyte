/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.scheduler.client;

import io.airbyte.workers.temporal.TemporalClient;
import io.airbyte.workers.temporal.TemporalClient.ManualOperationResult;
import java.util.Set;
import java.util.UUID;
import lombok.AllArgsConstructor;

@AllArgsConstructor
public class TemporalEventRunner implements EventRunner {

  private final TemporalClient temporalClient;

  public void createConnectionManagerWorkflow(final UUID connectionId) {
    temporalClient.submitConnectionUpdaterAsync(connectionId);
  }

  public ManualOperationResult startNewManualSync(final UUID connectionId) {
    return temporalClient.startNewManualSync(connectionId);
  }

  public ManualOperationResult startNewCancellation(final UUID connectionId) {
    return temporalClient.startNewCancellation(connectionId);
  }

  public ManualOperationResult resetConnection(final UUID connectionId) {
    return temporalClient.resetConnection(connectionId);
  }

  public ManualOperationResult synchronousResetConnection(final UUID connectionId) {
    return temporalClient.synchronousResetConnection(connectionId);
  }

  public void deleteConnection(final UUID connectionId) {
    temporalClient.deleteConnection(connectionId);
  }

  public void migrateSyncIfNeeded(final Set<UUID> connectionIds) {
    temporalClient.migrateSyncIfNeeded(connectionIds);
  }

  public void update(final UUID connectionId) {
    temporalClient.update(connectionId);
  }

}
