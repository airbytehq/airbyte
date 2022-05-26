/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.general;

import io.airbyte.config.StandardDiscoverCatalogInput;
import io.airbyte.protocol.models.AirbyteCatalog;
import io.airbyte.workers.Worker;

public interface DiscoverCatalogWorker extends Worker<StandardDiscoverCatalogInput, AirbyteCatalog> {}
