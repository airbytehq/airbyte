/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.general;

import io.airbyte.configoss.ConnectorJobOutput;
import io.airbyte.configoss.JobGetSpecConfig;
import io.airbyte.workers.TestHarness;

public interface GetSpecTestHarness extends TestHarness<JobGetSpecConfig, ConnectorJobOutput> {}
