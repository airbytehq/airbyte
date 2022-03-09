/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers;

import io.airbyte.config.StandardDiscoverCatalogInput;
import io.airbyte.protocol.models.AirbyteCatalog;

public interface DiscoverCatalogWorker extends Worker<StandardDiscoverCatalogInput, AirbyteCatalog> {}
