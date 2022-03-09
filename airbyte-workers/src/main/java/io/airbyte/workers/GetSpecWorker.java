/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers;

import io.airbyte.config.JobGetSpecConfig;
import io.airbyte.protocol.models.ConnectorSpecification;

public interface GetSpecWorker extends Worker<JobGetSpecConfig, ConnectorSpecification> {}
