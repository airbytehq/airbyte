/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.scheduler.client;

import io.airbyte.protocol.models.StreamDescriptor;
import io.airbyte.workers.temporal.TemporalClient.ManualOperationResult;
import java.util.List;
import java.util.Set;
import java.util.UUID;

public interface EventRunner {

  void createConnectionManagerWorkflow(final UUID connectionId);

  ManualOperationResult startNewManualSync(final UUID connectionId);

  ManualOperationResult startNewCancellation(final UUID connectionId);

  ManualOperationResult resetConnection(final UUID connectionId, final List<StreamDescriptor> streamsToReset);

  ManualOperationResult synchronousResetConnection(final UUID connectionId, final List<StreamDescriptor> streamsToReset);

  void deleteConnection(final UUID connectionId);

  void migrateSyncIfNeeded(final Set<UUID> connectionIds);

  void update(final UUID connectionId);

}
