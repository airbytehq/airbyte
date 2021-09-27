/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers;

import io.airbyte.config.StandardCheckConnectionInput;
import io.airbyte.config.StandardCheckConnectionOutput;

public interface CheckConnectionWorker extends Worker<StandardCheckConnectionInput, StandardCheckConnectionOutput> {}
