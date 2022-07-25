/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.general;

import io.airbyte.config.StandardCheckConnectionInput;
import io.airbyte.config.StandardCheckConnectionOutput;
import io.airbyte.workers.Worker;

public interface CheckConnectionWorker extends Worker<StandardCheckConnectionInput, StandardCheckConnectionOutput> {}
