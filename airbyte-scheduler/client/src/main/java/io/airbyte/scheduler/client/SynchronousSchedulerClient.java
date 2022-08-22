/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.scheduler.client;

import io.airbyte.config.DestinationConnection;
import io.airbyte.config.SourceConnection;
import io.airbyte.config.StandardCheckConnectionOutput;
import io.airbyte.protocol.models.AirbyteCatalog;
import io.airbyte.protocol.models.ConnectorSpecification;
import java.io.IOException;

/**
 * Exposes a way of executing short-lived jobs as RPC calls. Blocks until the job completes. No
 * metadata will be stored in the Jobs table for jobs triggered via this client.
 */
public interface SynchronousSchedulerClient {

  SynchronousResponse<StandardCheckConnectionOutput> createSourceCheckConnectionJob(SourceConnection source, String dockerImage)
      throws IOException;

  SynchronousResponse<StandardCheckConnectionOutput> createDestinationCheckConnectionJob(DestinationConnection destination, String dockerImage)
      throws IOException;

  SynchronousResponse<AirbyteCatalog> createDiscoverSchemaJob(SourceConnection source, String dockerImage) throws IOException;

  SynchronousResponse<ConnectorSpecification> createGetSpecJob(String dockerImage) throws IOException;

}
