/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.general;

import io.airbyte.config.ConnectorJobOutput;
import io.airbyte.config.StandardCheckConnectionInput;
import io.airbyte.commons.worker.Worker;

public interface CheckConnectionWorker extends Worker<StandardCheckConnectionInput, ConnectorJobOutput> {}
