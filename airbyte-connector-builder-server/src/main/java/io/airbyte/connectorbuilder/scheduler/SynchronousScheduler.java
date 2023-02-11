package io.airbyte.connectorbuilder.scheduler;

import io.airbyte.config.StandardConnectorBuilderReadOutput;
import java.io.IOException;

public interface SynchronousScheduler {
  SynchronousResponse<StandardConnectorBuilderReadOutput> createConnectorBuilderReadJob(String dockerImage) throws IOException;
}
