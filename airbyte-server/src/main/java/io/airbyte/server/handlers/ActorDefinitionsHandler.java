/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.handlers;

import static io.airbyte.server.ServerConstants.DEV_IMAGE_TAG;

import com.google.common.annotations.VisibleForTesting;
import io.airbyte.api.model.DestinationDefinitionIdRequestBody;
import io.airbyte.api.model.DestinationRead;
import io.airbyte.api.model.ReleaseStage;
import io.airbyte.api.model.SourceDefinitionIdRequestBody;
import io.airbyte.api.model.SourceRead;
import io.airbyte.commons.docker.DockerUtils;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.config.ActorDefinition;
import io.airbyte.config.ActorDefinition.ActorDefinitionReleaseStage;
import io.airbyte.config.ActorDefinition.ActorType;
import io.airbyte.config.ActorDefinitionResourceRequirements;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.protocol.models.ConnectorSpecification;
import io.airbyte.scheduler.client.SynchronousResponse;
import io.airbyte.scheduler.client.SynchronousSchedulerClient;
import io.airbyte.server.converters.SpecFetcher;
import io.airbyte.server.errors.InternalServerKnownException;
import io.airbyte.server.services.AirbyteGithubStore;
import io.airbyte.validation.json.JsonValidationException;
import java.io.IOException;
import java.net.URI;
import java.net.URISyntaxException;
import java.time.LocalDate;
import java.util.List;
import java.util.UUID;
import java.util.function.Supplier;
import java.util.stream.Collectors;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public abstract class ActorDefinitionsHandler<READ, LIST, CREATE, UPDATE, ID> {

  private static final Logger LOGGER = LoggerFactory.getLogger(ActorDefinitionsHandler.class);

  private final ConfigRepository configRepository;
  private final Supplier<UUID> uuidSupplier;
  private final SynchronousSchedulerClient schedulerSynchronousClient;
  private final AirbyteGithubStore githubStore;
  private final SourceHandler sourceHandler;
  private final DestinationHandler destinationHandler;
  private final ActorType actorType;

  public ActorDefinitionsHandler(final ConfigRepository configRepository,
                                 final SynchronousSchedulerClient schedulerSynchronousClient,
                                 final SourceHandler sourceHandler,
                                 final DestinationHandler destinationHandler,
                                 final ActorType actorType) {
    this(configRepository,
        UUID::randomUUID,
        schedulerSynchronousClient,
        AirbyteGithubStore.production(),
        sourceHandler,
        destinationHandler,
        actorType);
  }

  @VisibleForTesting
  public ActorDefinitionsHandler(final ConfigRepository configRepository,
                                 final Supplier<UUID> uuidSupplier,
                                 final SynchronousSchedulerClient schedulerSynchronousClient,
                                 final AirbyteGithubStore githubStore,
                                 final SourceHandler sourceHandler,
                                 final DestinationHandler destinationHandler,
                                 final ActorType actorType) {
    this.configRepository = configRepository;
    this.uuidSupplier = uuidSupplier;
    this.schedulerSynchronousClient = schedulerSynchronousClient;
    this.githubStore = githubStore;
    this.sourceHandler = sourceHandler;
    this.destinationHandler = destinationHandler;
    this.actorType = actorType;
  }

  abstract READ toRead(ActorDefinition actorDefinition);

  abstract ActorDefinition fromRead(READ read);

  abstract LIST toList(List<READ> reads);

  abstract ActorDefinition fromCreate(CREATE create);

  abstract ActorDefinition fromUpdate(UPDATE update);

  abstract UUID fromId(ID idRequest);

  public READ getActorDefinition(final ID idRequestBody) throws ConfigNotFoundException, IOException, JsonValidationException {
    return toRead(configRepository.getActorDefinition(fromId(idRequestBody), actorType));
  }

  public LIST listActorDefinitions() throws IOException, JsonValidationException {
    return toList(configRepository.listActorDefinitions(actorType, false)
        .stream()
        .map(this::toRead)
        .collect(Collectors.toList()));
  }

  public READ createCustomActorDefinition(final CREATE create) throws JsonValidationException, IOException {
    final ActorDefinition actorDefinition = fromCreate(create);

    final ConnectorSpecification spec = getSpecForImage(
        actorDefinition.getDockerRepository(),
        actorDefinition.getDockerImageTag());

    final UUID id = uuidSupplier.get();
    actorDefinition
        .withId(id)
        .withSpec(spec)
        .withTombstone(false)
        .withReleaseStage(ActorDefinitionReleaseStage.CUSTOM);

    configRepository.writeActorDefinition(actorDefinition);

    return toRead(actorDefinition);
  }

  public READ updateActorDefinition(final UPDATE update) throws ConfigNotFoundException, IOException, JsonValidationException {
    final ActorDefinition updateActorDefinition = fromUpdate(update);
    final ActorDefinition currentActorDefinition = configRepository.getActorDefinition(updateActorDefinition.getId(), actorType);

    // specs are re-fetched from the container if the image tag has changed, or if the tag is "dev",
    // to allow for easier iteration of dev images
    final boolean specNeedsUpdate = !currentActorDefinition.getDockerImageTag().equals(updateActorDefinition.getDockerImageTag())
        || updateActorDefinition.getDockerImageTag().equals(DEV_IMAGE_TAG);
    final ConnectorSpecification spec = specNeedsUpdate
        ? getSpecForImage(currentActorDefinition.getDockerRepository(), updateActorDefinition.getDockerImageTag())
        : currentActorDefinition.getSpec();
    final ActorDefinitionResourceRequirements updatedResourceReqs = updateActorDefinition.getResourceRequirements() != null
        ? updateActorDefinition.getResourceRequirements()
        : currentActorDefinition.getResourceRequirements();

    final ActorDefinition newActorDefinition = new ActorDefinition()
        .withId(currentActorDefinition.getId())
        .withDockerImageTag(updateActorDefinition.getDockerImageTag())
        .withDockerRepository(currentActorDefinition.getDockerRepository())
        .withName(currentActorDefinition.getName())
        .withDocumentationUrl(currentActorDefinition.getDocumentationUrl())
        .withIcon(currentActorDefinition.getIcon())
        .withSpec(spec)
        .withTombstone(currentActorDefinition.getTombstone())
        .withReleaseStage(currentActorDefinition.getReleaseStage())
        .withReleaseDate(currentActorDefinition.getReleaseDate())
        .withResourceRequirements(updatedResourceReqs);

    configRepository.writeActorDefinition(newActorDefinition);
    return toRead(newActorDefinition);
  }

  public void deleteActorDefinition(final ID idRequestBody) throws JsonValidationException, ConfigNotFoundException, IOException {
    /*
     * "delete" all destinations associated with the destination definition as well. This will cascade
     * to connections that depend on any deleted destinations. Delete destinations first in case a
     * failure occurs mid-operation.
     */
    final UUID actorDefinitionId = fromId(idRequestBody);
    final ActorDefinition persistedActorDefinition = configRepository.getActorDefinition(actorDefinitionId, actorType);

    // todo (cgardens) - remove when we consolidate SourceHandler and DestinationHandler
    if (actorType == ActorType.SOURCE) {
      final SourceDefinitionIdRequestBody destDefRequest = new SourceDefinitionIdRequestBody().sourceDefinitionId(actorDefinitionId);
      for (final SourceRead sourceRead : sourceHandler.listSourcesForSourceDefinition(destDefRequest).getSources()) {
        sourceHandler.deleteSource(sourceRead);
      }
    } else if (actorType == ActorType.DESTINATION) {
      final DestinationDefinitionIdRequestBody destDefRequest = new DestinationDefinitionIdRequestBody().destinationDefinitionId(actorDefinitionId);
      for (final DestinationRead destinationRead : destinationHandler.listDestinationsForDestinationDefinition(destDefRequest).getDestinations()) {
        destinationHandler.deleteDestination(destinationRead);
      }
    } else {
      throw new IllegalArgumentException("Unrecognized actor type");
    }

    persistedActorDefinition.withTombstone(true);
    configRepository.writeActorDefinition(persistedActorDefinition);
  }

  public LIST listLatestActorDefinitions() {
    if (actorType == ActorType.SOURCE) {
      return toList(getLatestSources()
          .stream()
          .map(this::toRead)
          .collect(Collectors.toList()));
    } else if (actorType == ActorType.DESTINATION) {
      return toList(getLatestDestinations()
          .stream()
          .map(this::toRead)
          .collect(Collectors.toList()));
    } else {
      throw new IllegalArgumentException("Unrecognized actor type");
    }
  }

  static URI getDocumentUri(final String documentationUrl) {
    try {
      return new URI(documentationUrl);
    } catch (final URISyntaxException | NullPointerException e) {
      throw new InternalServerKnownException("Unable to process retrieved latest source definitions list", e);
    }
  }

  static ReleaseStage getReleaseStage(final ActorDefinition actorDefinition) {
    if (actorDefinition.getReleaseStage() == null) {
      return null;
    }
    return ReleaseStage.fromValue(actorDefinition.getReleaseStage().value());
  }

  static LocalDate getReleaseDate(final ActorDefinition actorDefinition) {
    if (actorDefinition.getReleaseDate() == null || actorDefinition.getReleaseDate().isBlank()) {
      return null;
    }

    return LocalDate.parse(actorDefinition.getReleaseDate());
  }

  private List<ActorDefinition> getLatestSources() {
    try {
      return githubStore.getLatestSources();
    } catch (final InterruptedException e) {
      throw new InternalServerKnownException("Request to retrieve latest destination definitions failed", e);
    }
  }

  private List<ActorDefinition> getLatestDestinations() {
    try {
      return githubStore.getLatestDestinations();
    } catch (final InterruptedException e) {
      throw new InternalServerKnownException("Request to retrieve latest destination definitions failed", e);
    }
  }

  private ConnectorSpecification getSpecForImage(final String dockerRepository, final String imageTag) throws IOException {
    final String imageName = DockerUtils.getTaggedImageName(dockerRepository, imageTag);
    final SynchronousResponse<ConnectorSpecification> getSpecResponse = schedulerSynchronousClient.createGetSpecJob(imageName);
    return SpecFetcher.getSpecFromJob(getSpecResponse);
  }

  public static String loadIcon(final String name) {
    try {
      return name == null ? null : MoreResources.readResource("icons/" + name);
    } catch (final Exception e) {
      return null;
    }
  }

}
