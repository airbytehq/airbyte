/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.handlers;

import static io.airbyte.server.ServerConstants.DEV_IMAGE_TAG;

import com.google.common.annotations.VisibleForTesting;
import io.airbyte.api.model.generated.CustomDestinationDefinitionCreate;
import io.airbyte.api.model.generated.CustomDestinationDefinitionUpdate;
import io.airbyte.api.model.generated.DestinationDefinitionCreate;
import io.airbyte.api.model.generated.DestinationDefinitionIdRequestBody;
import io.airbyte.api.model.generated.DestinationDefinitionIdWithWorkspaceId;
import io.airbyte.api.model.generated.DestinationDefinitionRead;
import io.airbyte.api.model.generated.DestinationDefinitionReadList;
import io.airbyte.api.model.generated.DestinationDefinitionUpdate;
import io.airbyte.api.model.generated.DestinationRead;
import io.airbyte.api.model.generated.PrivateDestinationDefinitionRead;
import io.airbyte.api.model.generated.PrivateDestinationDefinitionReadList;
import io.airbyte.api.model.generated.ReleaseStage;
import io.airbyte.api.model.generated.WorkspaceIdRequestBody;
import io.airbyte.commons.docker.DockerUtils;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.commons.util.MoreLists;
import io.airbyte.config.ActorDefinitionResourceRequirements;
import io.airbyte.config.StandardDestinationDefinition;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.protocol.models.ConnectorSpecification;
import io.airbyte.scheduler.client.SynchronousResponse;
import io.airbyte.scheduler.client.SynchronousSchedulerClient;
import io.airbyte.server.converters.ApiPojoConverters;
import io.airbyte.server.converters.SpecFetcher;
import io.airbyte.server.errors.IdNotFoundKnownException;
import io.airbyte.server.errors.InternalServerKnownException;
import io.airbyte.server.services.AirbyteGithubStore;
import io.airbyte.validation.json.JsonValidationException;
import java.io.IOException;
import java.net.URI;
import java.net.URISyntaxException;
import java.time.LocalDate;
import java.util.List;
import java.util.Map.Entry;
import java.util.UUID;
import java.util.function.Supplier;
import java.util.stream.Collectors;

@SuppressWarnings("PMD.AvoidCatchingNPE")
public class DestinationDefinitionsHandler {

  private final ConfigRepository configRepository;
  private final Supplier<UUID> uuidSupplier;
  private final SynchronousSchedulerClient schedulerSynchronousClient;
  private final AirbyteGithubStore githubStore;
  private final DestinationHandler destinationHandler;

  public DestinationDefinitionsHandler(final ConfigRepository configRepository,
                                       final SynchronousSchedulerClient schedulerSynchronousClient,
                                       final DestinationHandler destinationHandler) {
    this(configRepository, UUID::randomUUID, schedulerSynchronousClient, AirbyteGithubStore.production(), destinationHandler);
  }

  @VisibleForTesting
  public DestinationDefinitionsHandler(final ConfigRepository configRepository,
                                       final Supplier<UUID> uuidSupplier,
                                       final SynchronousSchedulerClient schedulerSynchronousClient,
                                       final AirbyteGithubStore githubStore,
                                       final DestinationHandler destinationHandler) {
    this.configRepository = configRepository;
    this.uuidSupplier = uuidSupplier;
    this.schedulerSynchronousClient = schedulerSynchronousClient;
    this.githubStore = githubStore;
    this.destinationHandler = destinationHandler;
  }

  @VisibleForTesting
  static DestinationDefinitionRead buildDestinationDefinitionRead(final StandardDestinationDefinition standardDestinationDefinition) {
    try {
      return new DestinationDefinitionRead()
          .destinationDefinitionId(standardDestinationDefinition.getDestinationDefinitionId())
          .name(standardDestinationDefinition.getName())
          .dockerRepository(standardDestinationDefinition.getDockerRepository())
          .dockerImageTag(standardDestinationDefinition.getDockerImageTag())
          .documentationUrl(new URI(standardDestinationDefinition.getDocumentationUrl()))
          .icon(loadIcon(standardDestinationDefinition.getIcon()))
          .releaseStage(getReleaseStage(standardDestinationDefinition))
          .releaseDate(getReleaseDate(standardDestinationDefinition))
          .resourceRequirements(ApiPojoConverters.actorDefResourceReqsToApi(standardDestinationDefinition.getResourceRequirements()));
    } catch (final URISyntaxException | NullPointerException e) {
      throw new InternalServerKnownException("Unable to process retrieved latest destination definitions list", e);
    }
  }

  private static ReleaseStage getReleaseStage(final StandardDestinationDefinition standardDestinationDefinition) {
    if (standardDestinationDefinition.getReleaseStage() == null) {
      return null;
    }
    return ReleaseStage.fromValue(standardDestinationDefinition.getReleaseStage().value());
  }

  private static LocalDate getReleaseDate(final StandardDestinationDefinition standardDestinationDefinition) {
    if (standardDestinationDefinition.getReleaseDate() == null || standardDestinationDefinition.getReleaseDate().isBlank()) {
      return null;
    }

    return LocalDate.parse(standardDestinationDefinition.getReleaseDate());
  }

  public DestinationDefinitionReadList listDestinationDefinitions() throws IOException, JsonValidationException {
    return toDestinationDefinitionReadList(configRepository.listStandardDestinationDefinitions(false));
  }

  private static DestinationDefinitionReadList toDestinationDefinitionReadList(final List<StandardDestinationDefinition> defs) {
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
    } catch (final InterruptedException e) {
      throw new InternalServerKnownException("Request to retrieve latest destination definitions failed", e);
    }
  }

  public DestinationDefinitionReadList listDestinationDefinitionsForWorkspace(final WorkspaceIdRequestBody workspaceIdRequestBody)
      throws IOException {
    return toDestinationDefinitionReadList(MoreLists.concat(
        configRepository.listPublicDestinationDefinitions(false),
        configRepository.listGrantedDestinationDefinitions(workspaceIdRequestBody.getWorkspaceId(), false)));
  }

  public PrivateDestinationDefinitionReadList listPrivateDestinationDefinitions(final WorkspaceIdRequestBody workspaceIdRequestBody)
      throws IOException {
    final List<Entry<StandardDestinationDefinition, Boolean>> standardDestinationDefinitionBooleanMap =
        configRepository.listGrantableDestinationDefinitions(workspaceIdRequestBody.getWorkspaceId(), false);
    return toPrivateDestinationDefinitionReadList(standardDestinationDefinitionBooleanMap);
  }

  private static PrivateDestinationDefinitionReadList toPrivateDestinationDefinitionReadList(
                                                                                             final List<Entry<StandardDestinationDefinition, Boolean>> defs) {
    final List<PrivateDestinationDefinitionRead> reads = defs.stream()
        .map(entry -> new PrivateDestinationDefinitionRead()
            .destinationDefinition(buildDestinationDefinitionRead(entry.getKey()))
            .granted(entry.getValue()))
        .collect(Collectors.toList());
    return new PrivateDestinationDefinitionReadList().destinationDefinitions(reads);
  }

  public DestinationDefinitionRead getDestinationDefinition(final DestinationDefinitionIdRequestBody destinationDefinitionIdRequestBody)
      throws ConfigNotFoundException, IOException, JsonValidationException {
    return buildDestinationDefinitionRead(
        configRepository.getStandardDestinationDefinition(destinationDefinitionIdRequestBody.getDestinationDefinitionId()));
  }

  public DestinationDefinitionRead getDestinationDefinitionForWorkspace(
                                                                        final DestinationDefinitionIdWithWorkspaceId destinationDefinitionIdWithWorkspaceId)
      throws ConfigNotFoundException, IOException, JsonValidationException {
    final UUID definitionId = destinationDefinitionIdWithWorkspaceId.getDestinationDefinitionId();
    final UUID workspaceId = destinationDefinitionIdWithWorkspaceId.getWorkspaceId();
    if (!configRepository.workspaceCanUseDefinition(definitionId, workspaceId)) {
      throw new IdNotFoundKnownException("Cannot find the requested definition with given id for this workspace", definitionId.toString());
    }
    return getDestinationDefinition(new DestinationDefinitionIdRequestBody().destinationDefinitionId(definitionId));
  }

  public DestinationDefinitionRead createPrivateDestinationDefinition(final DestinationDefinitionCreate destinationDefCreate)
      throws JsonValidationException, IOException {
    final StandardDestinationDefinition destinationDefinition = destinationDefinitionFromCreate(destinationDefCreate)
        .withPublic(false)
        .withCustom(false);
    configRepository.writeStandardDestinationDefinition(destinationDefinition);

    return buildDestinationDefinitionRead(destinationDefinition);
  }

  public DestinationDefinitionRead createCustomDestinationDefinition(final CustomDestinationDefinitionCreate customDestinationDefinitionCreate)
      throws IOException {
    final StandardDestinationDefinition destinationDefinition = destinationDefinitionFromCreate(
        customDestinationDefinitionCreate.getDestinationDefinition())
            .withPublic(false)
            .withCustom(true);
    configRepository.writeCustomDestinationDefinition(destinationDefinition, customDestinationDefinitionCreate.getWorkspaceId());

    return buildDestinationDefinitionRead(destinationDefinition);
  }

  private StandardDestinationDefinition destinationDefinitionFromCreate(final DestinationDefinitionCreate destinationDefCreate) throws IOException {
    final ConnectorSpecification spec = getSpecForImage(
        destinationDefCreate.getDockerRepository(),
        destinationDefCreate.getDockerImageTag());

    final UUID id = uuidSupplier.get();
    final StandardDestinationDefinition destinationDefinition = new StandardDestinationDefinition()
        .withDestinationDefinitionId(id)
        .withDockerRepository(destinationDefCreate.getDockerRepository())
        .withDockerImageTag(destinationDefCreate.getDockerImageTag())
        .withDocumentationUrl(destinationDefCreate.getDocumentationUrl().toString())
        .withName(destinationDefCreate.getName())
        .withIcon(destinationDefCreate.getIcon())
        .withSpec(spec)
        .withTombstone(false)
        .withReleaseStage(StandardDestinationDefinition.ReleaseStage.CUSTOM)
        .withResourceRequirements(ApiPojoConverters.actorDefResourceReqsToInternal(destinationDefCreate.getResourceRequirements()));
    return destinationDefinition;
  }

  public DestinationDefinitionRead updateDestinationDefinition(final DestinationDefinitionUpdate destinationDefinitionUpdate)
      throws ConfigNotFoundException, IOException, JsonValidationException {
    final StandardDestinationDefinition currentDestination = configRepository
        .getStandardDestinationDefinition(destinationDefinitionUpdate.getDestinationDefinitionId());

    // specs are re-fetched from the container if the image tag has changed, or if the tag is "dev",
    // to allow for easier iteration of dev images
    final boolean specNeedsUpdate = !currentDestination.getDockerImageTag().equals(destinationDefinitionUpdate.getDockerImageTag())
        || destinationDefinitionUpdate.getDockerImageTag().equals(DEV_IMAGE_TAG);
    final ConnectorSpecification spec = specNeedsUpdate
        ? getSpecForImage(currentDestination.getDockerRepository(), destinationDefinitionUpdate.getDockerImageTag())
        : currentDestination.getSpec();
    final ActorDefinitionResourceRequirements updatedResourceReqs = destinationDefinitionUpdate.getResourceRequirements() != null
        ? ApiPojoConverters.actorDefResourceReqsToInternal(destinationDefinitionUpdate.getResourceRequirements())
        : currentDestination.getResourceRequirements();

    final StandardDestinationDefinition newDestination = new StandardDestinationDefinition()
        .withDestinationDefinitionId(currentDestination.getDestinationDefinitionId())
        .withDockerImageTag(destinationDefinitionUpdate.getDockerImageTag())
        .withDockerRepository(currentDestination.getDockerRepository())
        .withName(currentDestination.getName())
        .withDocumentationUrl(currentDestination.getDocumentationUrl())
        .withIcon(currentDestination.getIcon())
        .withSpec(spec)
        .withTombstone(currentDestination.getTombstone())
        .withPublic(currentDestination.getPublic())
        .withCustom(currentDestination.getCustom())
        .withReleaseStage(currentDestination.getReleaseStage())
        .withReleaseDate(currentDestination.getReleaseDate())
        .withResourceRequirements(updatedResourceReqs);

    configRepository.writeStandardDestinationDefinition(newDestination);
    return buildDestinationDefinitionRead(newDestination);
  }

  public DestinationDefinitionRead updateCustomDestinationDefinition(final CustomDestinationDefinitionUpdate customDestinationDefinitionUpdate)
      throws IOException, JsonValidationException, ConfigNotFoundException {
    final UUID definitionId = customDestinationDefinitionUpdate.getDestinationDefinition().getDestinationDefinitionId();
    final UUID workspaceId = customDestinationDefinitionUpdate.getWorkspaceId();
    if (!configRepository.workspaceCanUseCustomDefinition(definitionId, workspaceId)) {
      throw new IdNotFoundKnownException("Cannot find the requested definition with given id for this workspace", definitionId.toString());
    }
    return updateDestinationDefinition(customDestinationDefinitionUpdate.getDestinationDefinition());
  }

  public void deleteDestinationDefinition(final DestinationDefinitionIdRequestBody destinationDefinitionIdRequestBody)
      throws JsonValidationException, ConfigNotFoundException, IOException {
    // "delete" all destinations associated with the destination definition as well. This will cascade
    // to connections that depend on any deleted
    // destinations. Delete destinations first in case a failure occurs mid-operation.

    final StandardDestinationDefinition persistedDestinationDefinition =
        configRepository.getStandardDestinationDefinition(destinationDefinitionIdRequestBody.getDestinationDefinitionId());

    for (final DestinationRead destinationRead : destinationHandler.listDestinationsForDestinationDefinition(destinationDefinitionIdRequestBody)
        .getDestinations()) {
      destinationHandler.deleteDestination(destinationRead);
    }

    persistedDestinationDefinition.withTombstone(true);
    configRepository.writeStandardDestinationDefinition(persistedDestinationDefinition);
  }

  public void deleteCustomDestinationDefinition(final DestinationDefinitionIdWithWorkspaceId destinationDefinitionIdWithWorkspaceId)
      throws IOException, JsonValidationException, ConfigNotFoundException {
    final UUID definitionId = destinationDefinitionIdWithWorkspaceId.getDestinationDefinitionId();
    final UUID workspaceId = destinationDefinitionIdWithWorkspaceId.getWorkspaceId();
    if (!configRepository.workspaceCanUseCustomDefinition(definitionId, workspaceId)) {
      throw new IdNotFoundKnownException("Cannot find the requested definition with given id for this workspace", definitionId.toString());
    }
    deleteDestinationDefinition(new DestinationDefinitionIdRequestBody().destinationDefinitionId(definitionId));
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

  public PrivateDestinationDefinitionRead grantDestinationDefinitionToWorkspace(
                                                                                final DestinationDefinitionIdWithWorkspaceId destinationDefinitionIdWithWorkspaceId)
      throws JsonValidationException, ConfigNotFoundException, IOException {
    final StandardDestinationDefinition standardDestinationDefinition =
        configRepository.getStandardDestinationDefinition(destinationDefinitionIdWithWorkspaceId.getDestinationDefinitionId());
    configRepository.writeActorDefinitionWorkspaceGrant(
        destinationDefinitionIdWithWorkspaceId.getDestinationDefinitionId(),
        destinationDefinitionIdWithWorkspaceId.getWorkspaceId());
    return new PrivateDestinationDefinitionRead()
        .destinationDefinition(buildDestinationDefinitionRead(standardDestinationDefinition))
        .granted(true);
  }

  public void revokeDestinationDefinitionFromWorkspace(final DestinationDefinitionIdWithWorkspaceId destinationDefinitionIdWithWorkspaceId)
      throws IOException {
    configRepository.deleteActorDefinitionWorkspaceGrant(
        destinationDefinitionIdWithWorkspaceId.getDestinationDefinitionId(),
        destinationDefinitionIdWithWorkspaceId.getWorkspaceId());
  }

}
