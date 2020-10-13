package io.airbyte.server.validators;

import io.airbyte.commons.docker.DockerUtils;
import io.airbyte.server.errors.KnownException;
import io.airbyte.server.handlers.SchedulerHandler;

public class DockerImageValidator {

  private SchedulerHandler schedulerHandler;

  public DockerImageValidator (SchedulerHandler schedulerHandler){
    this.schedulerHandler = schedulerHandler;
  }

  /**
   * @throws KnownException if it is unable to verify that the input image is a valid connector definition image.
   */
  public void assertValidIntegrationImage(String dockerRepository, String imageTag) throws KnownException {
    // Validates that the docker image exists and can generate a compatible spec by running a getSpec
    // job on the provided image.
    String imageName = DockerUtils.getTaggedImageName(dockerRepository, imageTag);
    try {
      schedulerHandler.getConnectorSpecification(imageName);
    } catch (Exception e) {
      throw new KnownException(422, "Encountered an issue while validating input docker image: " + e.getMessage());
    }
  }
}
