/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.general;

import io.airbyte.config.JobGetSpecConfig;
import io.airbyte.protocol.models.ConnectorSpecification;
import io.airbyte.workers.Worker;

public interface GetSpecWorker extends Worker<JobGetSpecConfig, ConnectorSpecification> {}
