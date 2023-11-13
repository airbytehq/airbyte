/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.general;

import io.airbyte.configoss.ConnectorJobOutput;
import io.airbyte.configoss.StandardDiscoverCatalogInput;
import io.airbyte.workers.TestHarness;

public interface DiscoverCatalogTestHarness extends TestHarness<StandardDiscoverCatalogInput, ConnectorJobOutput> {}
