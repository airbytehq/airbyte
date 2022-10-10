/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.general;

import io.airbyte.config.ConnectorJobOutput;
import io.airbyte.config.JobGetSpecConfig;
import io.airbyte.commons.worker.Worker;

public interface GetSpecWorker extends Worker<JobGetSpecConfig, ConnectorJobOutput> {}
