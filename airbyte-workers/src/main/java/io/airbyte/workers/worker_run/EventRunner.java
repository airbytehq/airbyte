/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.worker_run;

import io.airbyte.api.model.ConnectionUpdate;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.validation.json.JsonValidationException;
import io.airbyte.workers.temporal.TemporalClient.ManualSyncSubmissionResult;
import java.io.IOException;
import java.util.Set;
import java.util.UUID;

public interface EventRunner {

  void createNewSchedulerWorkflow(final UUID connectionId);

  ManualSyncSubmissionResult startNewManualSync(final UUID connectionId);

  ManualSyncSubmissionResult startNewCancelation(final UUID connectionId);

  ManualSyncSubmissionResult resetConnection(final UUID connectionId);

  ManualSyncSubmissionResult synchronousResetConnection(final UUID connectionId);

  void deleteConnection(final UUID connectionId);

  void migrateSyncIfNeeded(final Set<UUID> connectionIds);

  void update(final ConnectionUpdate connectionUpdate) throws JsonValidationException, ConfigNotFoundException, IOException;

}
