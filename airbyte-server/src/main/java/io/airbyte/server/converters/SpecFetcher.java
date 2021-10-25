/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.converters;

import com.google.common.base.Preconditions;
import io.airbyte.commons.docker.DockerUtils;
import io.airbyte.config.JobConfig.ConfigType;
import io.airbyte.config.StandardDestinationDefinition;
import io.airbyte.config.StandardSourceDefinition;
import io.airbyte.protocol.models.ConnectorSpecification;
import io.airbyte.scheduler.client.SynchronousJobMetadata;
import io.airbyte.scheduler.client.SynchronousResponse;
import io.airbyte.scheduler.client.SynchronousSchedulerClient;
import java.io.IOException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class SpecFetcher {

  private static final Logger LOGGER = LoggerFactory.getLogger(SpecFetcher.class);

  private final SynchronousSchedulerClient schedulerJobClient;

  public SpecFetcher(final SynchronousSchedulerClient schedulerJobClient) {
    this.schedulerJobClient = schedulerJobClient;
  }

  // TODO: remove this once file migrations are deprecated, as that is the only time this function is
  // used
  @Deprecated
  public ConnectorSpecification getSpec(final String dockerImage) throws IOException {
    return getSpecFromJob(schedulerJobClient.createGetSpecJob(dockerImage));
  }

  public ConnectorSpecification getSpec(final StandardSourceDefinition sourceDefinition) throws IOException {
    return getSpecFromJob(getSpecJobResponse(sourceDefinition));
  }

  public ConnectorSpecification getSpec(final StandardDestinationDefinition destinationDefinition) throws IOException {
    return getSpecFromJob(getSpecJobResponse(destinationDefinition));
  }

  // TODO: remove this method once the spec is a required field on the StandardSourceDefinition struct
  public SynchronousResponse<ConnectorSpecification> getSpecJobResponse(final StandardSourceDefinition sourceDefinition) throws IOException {
    LOGGER.debug("Spec Fetcher: Getting spec for Source Definition.");
    final ConnectorSpecification spec = sourceDefinition.getSpec();

    if (spec != null) {
      LOGGER.debug("Spec Fetcher: Spec found in Source Definition.");
      return new SynchronousResponse<>(spec, SynchronousJobMetadata.mock(ConfigType.GET_SPEC));
    }

    LOGGER.debug("Spec Fetcher: Spec not found in Source Definition, fetching with scheduler job instead.");
    final String dockerImageName = DockerUtils.getTaggedImageName(sourceDefinition.getDockerRepository(), sourceDefinition.getDockerImageTag());
    return schedulerJobClient.createGetSpecJob(dockerImageName);
  }

  // TODO: remove this method once the spec is a required field on the StandardDestinationDefinition
  // struct
  public SynchronousResponse<ConnectorSpecification> getSpecJobResponse(final StandardDestinationDefinition destinationDefinition)
      throws IOException {
    LOGGER.debug("Spec Fetcher: Getting spec for Destination Definition.");
    final ConnectorSpecification spec = destinationDefinition.getSpec();

    if (spec != null) {
      LOGGER.debug("Spec Fetcher: Spec found in Destination Definition.");
      return new SynchronousResponse<>(spec, SynchronousJobMetadata.mock(ConfigType.GET_SPEC));
    }

    LOGGER.debug("Spec Fetcher: Spec not found in Destination Definition, fetching with scheduler job instead.");
    final String dockerImageName = DockerUtils.getTaggedImageName(
        destinationDefinition.getDockerRepository(),
        destinationDefinition.getDockerImageTag());
    return schedulerJobClient.createGetSpecJob(dockerImageName);
  }

  public static ConnectorSpecification getSpecFromJob(final SynchronousResponse<ConnectorSpecification> response) {
    Preconditions.checkState(response.isSuccess(), "Get Spec job failed.");
    Preconditions.checkNotNull(response.getOutput(), "Get Spec job return null spec");

    return response.getOutput();
  }

}
