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

import io.airbyte.api.model.DestinationIdRequestBody;
import io.airbyte.api.model.DestinationRead;
import io.airbyte.api.model.DestinationReadList;
import io.airbyte.api.model.DestinationUpdate;
import io.airbyte.commons.docker.DockerUtils;
import io.airbyte.commons.json.JsonValidationException;
import io.airbyte.config.StandardDestination;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.server.errors.KnownException;
import io.airbyte.server.validators.DockerImageValidator;

import java.io.IOException;
import java.net.URI;
import java.net.URISyntaxException;
import java.util.List;
import java.util.stream.Collectors;

public class DestinationsHandler {

  private final ConfigRepository configRepository;
  private DockerImageValidator dockerImageValidator;

  public DestinationsHandler(final ConfigRepository configRepository, DockerImageValidator dockerImageValidator) {
    this.configRepository = configRepository;
    this.dockerImageValidator = dockerImageValidator;
  }

  public DestinationReadList listDestinations()
      throws ConfigNotFoundException, IOException, JsonValidationException {
    final List<DestinationRead> reads = configRepository.listStandardDestinations()
        .stream()
        .map(DestinationsHandler::buildDestinationRead)
        .collect(Collectors.toList());

    return new DestinationReadList().destinations(reads);
  }

  public DestinationRead getDestination(DestinationIdRequestBody destinationIdRequestBody)
      throws ConfigNotFoundException, IOException, JsonValidationException {
    return buildDestinationRead(configRepository.getStandardDestination(destinationIdRequestBody.getDestinationId()));
  }

  public DestinationRead updateDestination(DestinationUpdate destinationUpdate) throws ConfigNotFoundException, IOException, JsonValidationException {
    StandardDestination currentDestination = configRepository.getStandardDestination(destinationUpdate.getDestinationId());
    dockerImageValidator.assertValidIntegrationImage(currentDestination.getDockerRepository(), destinationUpdate.getDockerImageTag());

    StandardDestination newDestination = new StandardDestination()
        .withDestinationId(currentDestination.getDestinationId())
        .withDockerImageTag(destinationUpdate.getDockerImageTag())
        .withDockerRepository(currentDestination.getDockerRepository())
        .withName(currentDestination.getName())
        .withDocumentationUrl(currentDestination.getDocumentationUrl());

    configRepository.writeStandardDestination(newDestination);
    return buildDestinationRead(newDestination);
  }

  private static DestinationRead buildDestinationRead(StandardDestination standardDestination) {
    try {
      return new DestinationRead()
          .destinationId(standardDestination.getDestinationId())
          .name(standardDestination.getName())
          .dockerRepository(standardDestination.getDockerRepository())
          .dockerImageTag(standardDestination.getDockerImageTag())
          .documentationUrl(new URI(standardDestination.getDocumentationUrl()));
    } catch (URISyntaxException e) {
      throw new RuntimeException(e);
    }
  }
}
