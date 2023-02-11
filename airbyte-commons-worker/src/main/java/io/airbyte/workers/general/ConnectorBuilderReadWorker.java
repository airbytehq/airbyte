/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.general;

import io.airbyte.config.StandardConnectorBuilderReadInput;
import io.airbyte.config.StandardConnectorBuilderReadOutput;
import io.airbyte.workers.Worker;

public interface ConnectorBuilderReadWorker extends Worker<StandardConnectorBuilderReadInput, StandardConnectorBuilderReadOutput> {

}
