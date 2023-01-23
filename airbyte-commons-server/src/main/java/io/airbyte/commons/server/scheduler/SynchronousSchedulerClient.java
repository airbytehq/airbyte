/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.server.scheduler;

import io.airbyte.commons.version.Version;
import io.airbyte.config.DestinationConnection;
import io.airbyte.config.SourceConnection;
import io.airbyte.config.StandardCheckConnectionOutput;
import io.airbyte.protocol.models.ConnectorSpecification;
import java.io.IOException;
import java.util.UUID;

/**
 * Exposes a way of executing short-lived jobs as RPC calls. Blocks until the job completes. No
 * metadata will be stored in the Jobs table for jobs triggered via this client.
 */
public interface SynchronousSchedulerClient {

  SynchronousResponse<StandardCheckConnectionOutput> createSourceCheckConnectionJob(SourceConnection source,
                                                                                    String dockerImage,
                                                                                    Version protocolVersion,
                                                                                    boolean isCustomConnector)
      throws IOException;

  SynchronousResponse<StandardCheckConnectionOutput> createDestinationCheckConnectionJob(DestinationConnection destination,
                                                                                         String dockerImage,
                                                                                         Version protocolVersion,
                                                                                         boolean isCustomConnector)
      throws IOException;

  SynchronousResponse<UUID> createDiscoverSchemaJob(SourceConnection source,
                                                    String dockerImage,
                                                    String connectorVersion,
                                                    Version protocolVersion,
                                                    boolean isCustomConnector)
      throws IOException;

  SynchronousResponse<ConnectorSpecification> createGetSpecJob(String dockerImage, boolean isCustomConnector) throws IOException;

}
