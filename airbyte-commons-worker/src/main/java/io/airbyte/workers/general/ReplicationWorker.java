/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.general;

import io.airbyte.config.ReplicationOutput;
import io.airbyte.config.StandardSyncInput;
import io.airbyte.workers.Worker;

public interface ReplicationWorker extends Worker<StandardSyncInput, ReplicationOutput> {}
