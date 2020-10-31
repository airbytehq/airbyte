/*
 * MIT License
 *
 * Copyright (c) 2020 Airbyte
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 */

package io.airbyte.server.handlers;

import io.airbyte.api.model.DestinationDefinitionIdRequestBody;
import io.airbyte.api.model.DestinationDefinitionRead;
import io.airbyte.api.model.DestinationDefinitionReadList;
import io.airbyte.api.model.DestinationDefinitionUpdate;
import io.airbyte.config.StandardDestination;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.server.validators.DockerImageValidator;
import io.airbyte.validation.json.JsonValidationException;
import java.io.IOException;
import java.net.URI;
import java.net.URISyntaxException;
import java.util.List;
import java.util.stream.Collectors;

public class DestinationDefinitionsHandler {

  private final ConfigRepository configRepository;
  private DockerImageValidator dockerImageValidator;

  public DestinationDefinitionsHandler(final ConfigRepository configRepository, DockerImageValidator dockerImageValidator) {
    this.configRepository = configRepository;
    this.dockerImageValidator = dockerImageValidator;
  }

  public DestinationDefinitionReadList listDestinationDefinitions()
      throws ConfigNotFoundException, IOException, JsonValidationException {
    final List<DestinationDefinitionRead> reads = configRepository.listStandardDestinations()
        .stream()
        .map(DestinationDefinitionsHandler::buildDestinationDefinitionRead)
        .collect(Collectors.toList());

    return new DestinationDefinitionReadList().destinationDefinitions(reads);
  }

  public DestinationDefinitionRead getDestinationDefinition(DestinationDefinitionIdRequestBody destinationDefinitionIdRequestBody)
      throws ConfigNotFoundException, IOException, JsonValidationException {
    return buildDestinationDefinitionRead(configRepository.getStandardDestination(destinationDefinitionIdRequestBody.getDestinationDefinitionId()));
  }

  public DestinationDefinitionRead updateDestinationDefinition(DestinationDefinitionUpdate destinationDefinitionUpdate)
      throws ConfigNotFoundException, IOException, JsonValidationException {
    StandardDestination currentDestination = configRepository.getStandardDestination(destinationDefinitionUpdate.getDestinationDefinitionId());
    dockerImageValidator.assertValidIntegrationImage(currentDestination.getDockerRepository(), destinationDefinitionUpdate.getDockerImageTag());

    StandardDestination newDestination = new StandardDestination()
        .withDestinationId(currentDestination.getDestinationId())
        .withDockerImageTag(destinationDefinitionUpdate.getDockerImageTag())
        .withDockerRepository(currentDestination.getDockerRepository())
        .withName(currentDestination.getName())
        .withDocumentationUrl(currentDestination.getDocumentationUrl());

    configRepository.writeStandardDestination(newDestination);
    return buildDestinationDefinitionRead(newDestination);
  }

  private static DestinationDefinitionRead buildDestinationDefinitionRead(StandardDestination standardDestination) {
    try {
      return new DestinationDefinitionRead()
          .destinationDefinitionId(standardDestination.getDestinationId())
          .name(standardDestination.getName())
          .dockerRepository(standardDestination.getDockerRepository())
          .dockerImageTag(standardDestination.getDockerImageTag())
          .documentationUrl(new URI(standardDestination.getDocumentationUrl()));
    } catch (URISyntaxException e) {
      throw new RuntimeException(e);
    }
  }

}
