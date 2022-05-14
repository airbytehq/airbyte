/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.scheduler.client;

import io.airbyte.workers.temporal.TemporalClient.ManualOperationResult;
import java.util.Set;
import java.util.UUID;

public interface EventRunner {

  void createNewSchedulerWorkflow(final UUID connectionId);

  ManualOperationResult startNewManualSync(final UUID connectionId);

  ManualOperationResult startNewCancellation(final UUID connectionId);

  ManualOperationResult resetConnection(final UUID connectionId);

  ManualOperationResult synchronousResetConnection(final UUID connectionId);

  void deleteConnection(final UUID connectionId);

  void migrateSyncIfNeeded(final Set<UUID> connectionIds);

  void update(final UUID connectionId);

}
