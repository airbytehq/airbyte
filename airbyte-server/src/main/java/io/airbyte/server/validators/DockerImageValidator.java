/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.validators;

import io.airbyte.commons.docker.DockerUtils;
import io.airbyte.protocol.models.ConnectorSpecification;
import io.airbyte.scheduler.client.SynchronousResponse;
import io.airbyte.scheduler.client.SynchronousSchedulerClient;
import io.airbyte.server.converters.SpecFetcher;
import io.airbyte.server.errors.BadObjectSchemaKnownException;

public class DockerImageValidator {

  private final SynchronousSchedulerClient schedulerClient;

  public DockerImageValidator(final SynchronousSchedulerClient schedulerJobClient) {
    this.schedulerClient = schedulerJobClient;
  }

  /**
   * @throws BadObjectSchemaKnownException if it is unable to verify that the input image is a valid
   *         connector definition image.
   */
  public void assertValidIntegrationImage(final String dockerRepository, final String imageTag) throws BadObjectSchemaKnownException {
    // Validates that the docker image exists and can generate a compatible spec by running a getSpec
    // job on the provided image.
    final String imageName = DockerUtils.getTaggedImageName(dockerRepository, imageTag);
    try {
      final SynchronousResponse<ConnectorSpecification> getSpecResponse = schedulerClient.createGetSpecJob(imageName);
      SpecFetcher.getSpecFromJob(getSpecResponse);
    } catch (final Exception e) {
      throw new BadObjectSchemaKnownException(
          String.format("Encountered an issue while validating input docker image (%s): %s", imageName, e.getMessage()));
    }
  }

}
