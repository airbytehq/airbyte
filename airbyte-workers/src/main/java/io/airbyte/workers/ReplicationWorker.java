/*
 * Copyright (c) 2020 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers;

import io.airbyte.config.ReplicationOutput;
import io.airbyte.config.StandardSyncInput;

public interface ReplicationWorker extends Worker<StandardSyncInput, ReplicationOutput> {}
