/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.connectorbuilder.scheduler;

import io.airbyte.config.StandardConnectorBuilderReadOutput;
import java.io.IOException;
import java.util.UUID;

public interface SynchronousScheduler {

  SynchronousResponse<StandardConnectorBuilderReadOutput> createConnectorBuilderReadJob(UUID workspaceID, String dockerImage) throws IOException;

}
