/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.converters;

import com.google.common.base.Preconditions;
import io.airbyte.commons.docker.DockerUtils;
import io.airbyte.config.StandardDestinationDefinition;
import io.airbyte.config.StandardSourceDefinition;
import io.airbyte.protocol.models.ConnectorSpecification;
import io.airbyte.scheduler.client.SynchronousResponse;
import io.airbyte.scheduler.client.SynchronousSchedulerClient;
import java.io.IOException;

public class SpecFetcher {

  private final SynchronousSchedulerClient schedulerJobClient;

  public SpecFetcher(final SynchronousSchedulerClient schedulerJobClient) {
    this.schedulerJobClient = schedulerJobClient;
  }

  public ConnectorSpecification execute(final String dockerImage) throws IOException {
    return getSpecFromJob(schedulerJobClient.createGetSpecJob(dockerImage));
  }

  public ConnectorSpecification execute(final StandardSourceDefinition sourceDefinition) throws IOException {
    final ConnectorSpecification spec = sourceDefinition.getSpec();

    if (spec != null) {
      return spec;
    }

    final String dockerImageName = DockerUtils.getTaggedImageName(sourceDefinition.getDockerRepository(), sourceDefinition.getDockerImageTag());
    return getSpecFromJob(schedulerJobClient.createGetSpecJob(dockerImageName));
  }

  public ConnectorSpecification execute(final StandardDestinationDefinition sourceDefinition) throws IOException {
    final ConnectorSpecification spec = sourceDefinition.getSpec();

    if (spec != null) {
      return spec;
    }

    final String dockerImageName = DockerUtils.getTaggedImageName(sourceDefinition.getDockerRepository(), sourceDefinition.getDockerImageTag());
    return getSpecFromJob(schedulerJobClient.createGetSpecJob(dockerImageName));
  }

  private static ConnectorSpecification getSpecFromJob(final SynchronousResponse<ConnectorSpecification> response) {
    Preconditions.checkState(response.isSuccess(), "Get Spec job failed.");
    Preconditions.checkNotNull(response.getOutput(), "Get Spec job return null spec");

    return response.getOutput();
  }

}
