/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.general;

import io.airbyte.config.StandardDiscoverCatalogInput;
import io.airbyte.config.StandardDiscoverCatalogOutput;
import io.airbyte.workers.Worker;

public interface DiscoverCatalogWorker extends Worker<StandardDiscoverCatalogInput, StandardDiscoverCatalogOutput> {}
