/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.handlers;

import static io.airbyte.server.ServerConstants.DEV_IMAGE_TAG;

import io.airbyte.api.model.ReleaseStage;
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
  final ActorType actorType;

  public ActorDefinitionsHandler(final ConfigRepository configRepository,
                                 final SynchronousSchedulerClient schedulerSynchronousClient,
                                 final ActorType actorType) {
    this(configRepository,
        UUID::randomUUID,
        schedulerSynchronousClient,
        AirbyteGithubStore.production(),
        actorType);
  }

  public ActorDefinitionsHandler(final ConfigRepository configRepository,
                                 final Supplier<UUID> uuidSupplier,
                                 final SynchronousSchedulerClient schedulerSynchronousClient,
                                 final AirbyteGithubStore githubStore,
                                 final ActorType actorType) {
    this.configRepository = configRepository;
    this.uuidSupplier = uuidSupplier;
    this.schedulerSynchronousClient = schedulerSynchronousClient;
    this.githubStore = githubStore;
    this.actorType = actorType;
  }

  /**
   * Convert from an ActorDefinition to the API read struct for the resource.
   *
   * @param actorDefinition - actor definition to convert
   * @return API read struct
   */
  abstract READ toRead(ActorDefinition actorDefinition);

  /**
   * For a resource, convert from a list of API read structs to an API list struct.
   *
   * @param reads - API read structs to convert
   * @return API list struct
   */
  abstract LIST toList(List<READ> reads);

  /**
   * Convert from a resource's API create struct to a PARTIAL ActorDefinition. The following fields do
   * not need to be filled: id, spec. They are filled by the internals of the create method.
   *
   * @param create - API create struct to convert
   * @return API create struct represented as an actor definition
   */
  abstract ActorDefinition fromCreate(CREATE create);

  /**
   * Convert from a resource's API update struct to a PARTIAL ActorDefinition. Only the following
   * fields will be set: actorType, id, dockerImageTag, resourceRequirements. All others are not
   * updatable by the end user and will be set or overwritten by the internals of the update method.
   *
   * @param update - API update struct to convert
   * @return API update struct represented as an actor definition
   */
  abstract ActorDefinition fromUpdate(UPDATE update);

  /**
   * Convert from a resource's API id struct to the actual id (as a UUID).
   *
   * @param idRequest - API id struct to convert
   * @return extracted id
   */
  abstract UUID fromId(ID idRequest);

  /**
   * When deleting an actor definition, we usually want to disable all actors associated with that
   * definition. This method should overridden to carry that out.
   *
   * @param definitionId - definition id whose children will be targeted
   */
  abstract void deleteChildren(UUID definitionId) throws JsonValidationException, ConfigNotFoundException, IOException;

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
        .withActorType(actorType)
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
     * "delete" all actors associated with the actor definition as well. This will cascade to
     * connections that depend on any deleted actors. Delete actors first in case a failure occurs
     * mid-operation.
     */
    final UUID actorDefinitionId = fromId(idRequestBody);
    final ActorDefinition persistedActorDefinition = configRepository.getActorDefinition(actorDefinitionId, actorType);

    deleteChildren(actorDefinitionId);

    persistedActorDefinition.withTombstone(true);
    configRepository.writeActorDefinition(persistedActorDefinition);
  }

  public LIST listLatestActorDefinitions() {
    return toList(getLatestDefinitions(actorType)
        .stream()
        .map(this::toRead)
        .collect(Collectors.toList()));
  }

  static URI getDocumentUri(final String documentationUrl) {
    try {
      return new URI(documentationUrl);
    } catch (final URISyntaxException | NullPointerException e) {
      throw new InternalServerKnownException(String.format("Unable to create documentationUrl for url: %s", documentationUrl), e);
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

  private List<ActorDefinition> getLatestDefinitions(final ActorType actorType) {
    try {
      return githubStore.getLatestDefinitions(actorType);
    } catch (final InterruptedException e) {
      throw new InternalServerKnownException("Request to retrieve latest actor definitions failed", e);
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
