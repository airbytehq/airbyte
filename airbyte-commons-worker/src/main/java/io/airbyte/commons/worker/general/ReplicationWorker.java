/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.worker.general;

import io.airbyte.commons.worker.Worker;
import io.airbyte.config.ReplicationOutput;
import io.airbyte.config.StandardSyncInput;

public interface ReplicationWorker extends Worker<StandardSyncInput, ReplicationOutput> {}
