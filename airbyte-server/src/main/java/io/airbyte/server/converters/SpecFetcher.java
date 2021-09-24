/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.converters;

import com.google.common.base.Preconditions;
import io.airbyte.protocol.models.ConnectorSpecification;
import io.airbyte.scheduler.client.SynchronousResponse;
import io.airbyte.scheduler.client.SynchronousSchedulerClient;
import java.io.IOException;

public class SpecFetcher {

  private final SynchronousSchedulerClient schedulerJobClient;

  public SpecFetcher(SynchronousSchedulerClient schedulerJobClient) {
    this.schedulerJobClient = schedulerJobClient;
  }

  public ConnectorSpecification execute(String dockerImage) throws IOException {
    return getSpecFromJob(schedulerJobClient.createGetSpecJob(dockerImage));
  }

  private static ConnectorSpecification getSpecFromJob(SynchronousResponse<ConnectorSpecification> response) {
    Preconditions.checkState(response.isSuccess(), "Get Spec job failed.");
    Preconditions.checkNotNull(response.getOutput(), "Get Spec job return null spec");

    return response.getOutput();
  }

}
