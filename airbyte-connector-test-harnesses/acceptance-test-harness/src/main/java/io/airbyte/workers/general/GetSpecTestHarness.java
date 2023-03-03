/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.general;

import io.airbyte.config.ConnectorJobOutput;
import io.airbyte.config.JobGetSpecConfig;
import io.airbyte.workers.TestHarness;

public interface GetSpecTestHarness extends TestHarness<JobGetSpecConfig, ConnectorJobOutput> {}
