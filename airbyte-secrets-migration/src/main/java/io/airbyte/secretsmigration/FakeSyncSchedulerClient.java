/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.secretsmigration;

import io.airbyte.config.DestinationConnection;
import io.airbyte.config.SourceConnection;
import io.airbyte.config.StandardCheckConnectionOutput;
import io.airbyte.protocol.models.AirbyteCatalog;
import io.airbyte.protocol.models.ConnectorSpecification;
import io.airbyte.scheduler.client.SynchronousResponse;
import io.airbyte.scheduler.client.SynchronousSchedulerClient;
import java.io.IOException;
import org.apache.commons.lang3.NotImplementedException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class FakeSyncSchedulerClient implements SynchronousSchedulerClient {

  private static final Logger LOGGER = LoggerFactory.getLogger(FakeSyncSchedulerClient.class);

  @Override
  public SynchronousResponse<StandardCheckConnectionOutput> createSourceCheckConnectionJob(SourceConnection source, String dockerImage)
      throws IOException {
    throw new NotImplementedException();
  }

  @Override
  public SynchronousResponse<StandardCheckConnectionOutput> createDestinationCheckConnectionJob(DestinationConnection destination, String dockerImage)
      throws IOException {
    throw new NotImplementedException();
  }

  @Override
  public SynchronousResponse<AirbyteCatalog> createDiscoverSchemaJob(SourceConnection source, String dockerImage) throws IOException {
    throw new NotImplementedException();
  }

  @Override
  public SynchronousResponse<ConnectorSpecification> createGetSpecJob(String dockerImage) throws IOException {
    LOGGER.error("spec cache not available for: " + dockerImage);
    throw new NotImplementedException();
  }

}
