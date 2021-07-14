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

import com.google.common.annotations.VisibleForTesting;
import com.google.common.base.Preconditions;
import io.airbyte.api.model.*;
import io.airbyte.commons.docker.DockerUtils;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.config.StandardDestinationDefinition;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.protocol.models.ConnectorSpecification;
import io.airbyte.scheduler.client.CachingSynchronousSchedulerClient;
import io.airbyte.scheduler.client.SynchronousResponse;
import io.airbyte.server.converters.JobConverter;
import io.airbyte.server.converters.SpecFetcher;
import io.airbyte.server.errors.BadObjectSchemaKnownException;
import io.airbyte.server.errors.InternalServerKnownException;
import io.airbyte.server.errors.KnownException;
import io.airbyte.server.services.AirbyteGithubStore;
import io.airbyte.validation.json.JsonValidationException;
import java.io.IOException;
import java.net.URI;
import java.net.URISyntaxException;
import java.util.List;
import java.util.UUID;
import java.util.function.Supplier;
import java.util.stream.Collectors;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class DestinationDefinitionsHandler {

  private static final Logger LOGGER = LoggerFactory.getLogger(DestinationDefinitionsHandler.class);

  private final ConfigRepository configRepository;
  private final Supplier<UUID> uuidSupplier;
  private final SpecFetcher specFetcher;
  private final CachingSynchronousSchedulerClient schedulerSynchronousClient;
  private final AirbyteGithubStore githubStore;

  public DestinationDefinitionsHandler(final ConfigRepository configRepository,
                                       final SpecFetcher specFetcher,
                                       final CachingSynchronousSchedulerClient schedulerSynchronousClient) {
    this(configRepository, UUID::randomUUID, specFetcher, schedulerSynchronousClient, AirbyteGithubStore.production());
  }

  @VisibleForTesting
  public DestinationDefinitionsHandler(final ConfigRepository configRepository,
                                       final Supplier<UUID> uuidSupplier,
                                       final SpecFetcher specFetcher,
                                       final CachingSynchronousSchedulerClient schedulerSynchronousClient,
                                       final AirbyteGithubStore githubStore) {
    this.configRepository = configRepository;
    this.specFetcher = specFetcher;
    this.uuidSupplier = uuidSupplier;
    this.schedulerSynchronousClient = schedulerSynchronousClient;
    this.githubStore = githubStore;
  }

  @VisibleForTesting
  static DestinationDefinitionRead buildDestinationDefinitionRead(StandardDestinationDefinition standardDestinationDefinition) {
    try {
      return new DestinationDefinitionRead()
          .destinationDefinitionId(standardDestinationDefinition.getDestinationDefinitionId())
          .name(standardDestinationDefinition.getName())
          .dockerRepository(standardDestinationDefinition.getDockerRepository())
          .dockerImageTag(standardDestinationDefinition.getDockerImageTag())
          .documentationUrl(new URI(standardDestinationDefinition.getDocumentationUrl()))
          .icon(loadIcon(standardDestinationDefinition.getIcon()));
    } catch (URISyntaxException | NullPointerException e) {
      throw new InternalServerKnownException("Unable to process retrieved latest destination definitions list", e);
    }
  }

  public DestinationDefinitionReadList listDestinationDefinitions() throws IOException, JsonValidationException {
    return toDestinationDefinitionReadList(configRepository.listStandardDestinationDefinitions());
  }

  private static DestinationDefinitionReadList toDestinationDefinitionReadList(List<StandardDestinationDefinition> defs) {
    final List<DestinationDefinitionRead> reads = defs.stream()
        .map(DestinationDefinitionsHandler::buildDestinationDefinitionRead)
        .collect(Collectors.toList());
    return new DestinationDefinitionReadList().destinationDefinitions(reads);
  }

  public DestinationDefinitionReadList listLatestDestinationDefinitions() {
    return toDestinationDefinitionReadList(getLatestDestinations());
  }

  private List<StandardDestinationDefinition> getLatestDestinations() {
    try {
      return githubStore.getLatestDestinations();
    } catch (InterruptedException e) {
      throw new InternalServerKnownException("Request to retrieve latest destination definitions failed", e);
    }
  }

  public DestinationDefinitionRead getDestinationDefinition(DestinationDefinitionIdRequestBody destinationDefinitionIdRequestBody)
      throws ConfigNotFoundException, IOException, JsonValidationException {
    return buildDestinationDefinitionRead(
        configRepository.getStandardDestinationDefinition(destinationDefinitionIdRequestBody.getDestinationDefinitionId()));
  }

  public DestinationDefinitionReadWithJobInfo createDestinationDefinition(DestinationDefinitionCreate destinationDefinitionCreate)
      throws JsonValidationException, IOException {
    final UUID id = uuidSupplier.get();
    final StandardDestinationDefinition destinationDefinition = new StandardDestinationDefinition()
        .withDestinationDefinitionId(id)
        .withDockerRepository(destinationDefinitionCreate.getDockerRepository())
        .withDockerImageTag(destinationDefinitionCreate.getDockerImageTag())
        .withDocumentationUrl(destinationDefinitionCreate.getDocumentationUrl().toString())
        .withName(destinationDefinitionCreate.getName())
        .withIcon(destinationDefinitionCreate.getIcon());

    // Validates that the docker image exists and can generate a compatible spec by running a getSpec
    // job on the provided image and checking that getOutput() worked. If it succeeds, then writes the
    // config.
    SynchronousResponse<ConnectorSpecification> response = null;
    KnownException validationException = null;
    try {
      response = specFetcher.executeWithResponse(
          DockerUtils.getTaggedImageName(destinationDefinitionCreate.getDockerRepository(), destinationDefinitionCreate.getDockerImageTag()));
      Preconditions.checkNotNull(response, "Get Spec from connector docker image job returned null response");
      Preconditions.checkState(response.isSuccess(), "Get Spec from connector docker image job failed.");
      Preconditions.checkNotNull(response.getOutput(), "Get Spec from connector docker image job return null spec");

      configRepository.writeStandardDestinationDefinition(destinationDefinition);
    } catch (NullPointerException e) {
      validationException = new BadObjectSchemaKnownException(
          String.format("Encountered an issue while validating input docker image from %s:%s - %s",
              destinationDefinitionCreate.getDockerRepository(),
              destinationDefinitionCreate.getDockerImageTag(),
              e.toString() + " " + e.getMessage()),
          e);
    }

    // When an error occurs, your destination isn't echoed back to you, indicating it failed to save.
    return new DestinationDefinitionReadWithJobInfo()
        .exception(validationException == null ? null : validationException.getKnownExceptionInfo())
        .destinationDefinitionRead(validationException != null ? null : buildDestinationDefinitionRead(destinationDefinition))
        .jobInfo(JobConverter.getSynchronousJobRead(response));
  }

  public DestinationDefinitionReadWithJobInfo updateDestinationDefinition(DestinationDefinitionUpdate destinationDefinitionUpdate)
      throws ConfigNotFoundException, IOException, JsonValidationException {
    final StandardDestinationDefinition currentDestination = configRepository
        .getStandardDestinationDefinition(destinationDefinitionUpdate.getDestinationDefinitionId());

    final StandardDestinationDefinition newDestination = new StandardDestinationDefinition()
        .withDestinationDefinitionId(currentDestination.getDestinationDefinitionId())
        .withDockerImageTag(destinationDefinitionUpdate.getDockerImageTag())
        .withDockerRepository(currentDestination.getDockerRepository())
        .withName(currentDestination.getName())
        .withDocumentationUrl(currentDestination.getDocumentationUrl())
        .withIcon(currentDestination.getIcon());

    // Validates that the docker image exists and can generate a compatible spec by running a getSpec
    // job on the provided image and checking that getOutput() worked. If it passes, then saves the
    // config.
    SynchronousResponse<ConnectorSpecification> response = null;
    KnownException validationException = null;
    try {
      response = specFetcher.executeWithResponse(
          DockerUtils.getTaggedImageName(currentDestination.getDockerRepository(), destinationDefinitionUpdate.getDockerImageTag()));
      Preconditions.checkNotNull(response, "Get Spec job returned null response");
      Preconditions.checkState(response.isSuccess(), "Get Spec job failed.");
      Preconditions.checkNotNull(response.getOutput(), "Get Spec job return null spec");

      configRepository.writeStandardDestinationDefinition(newDestination);
      // we want to re-fetch the spec for updated definitions.
      schedulerSynchronousClient.resetCache();
    } catch (NullPointerException e) {
      validationException =
          new BadObjectSchemaKnownException(String.format("Encountered an issue while validating input docker image from %s:%s - %s",
              currentDestination.getDockerRepository(), destinationDefinitionUpdate.getDockerImageTag(), e.toString() + " " + e.getMessage()), e);
    }

    // When an error occurs, your destination isn't echoed back to you, indicating it failed to save.
    return new DestinationDefinitionReadWithJobInfo()
        .exception(validationException == null ? null : validationException.getKnownExceptionInfo())
        .destinationDefinitionRead(validationException != null ? null : buildDestinationDefinitionRead(newDestination))
        .jobInfo(JobConverter.getSynchronousJobRead(response));
  }

  public static String loadIcon(String name) {
    try {
      return name == null ? null : MoreResources.readResource("icons/" + name);
    } catch (Exception e) {
      return null;
    }
  }

}
