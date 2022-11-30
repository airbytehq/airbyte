/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.handlers;

import static io.airbyte.server.ServerConstants.DEV_IMAGE_TAG;

import com.google.common.annotations.VisibleForTesting;
import io.airbyte.api.model.generated.CustomSourceDefinitionCreate;
import io.airbyte.api.model.generated.CustomSourceDefinitionUpdate;
import io.airbyte.api.model.generated.PrivateSourceDefinitionRead;
import io.airbyte.api.model.generated.PrivateSourceDefinitionReadList;
import io.airbyte.api.model.generated.ReleaseStage;
import io.airbyte.api.model.generated.SourceDefinitionCreate;
import io.airbyte.api.model.generated.SourceDefinitionIdRequestBody;
import io.airbyte.api.model.generated.SourceDefinitionIdWithWorkspaceId;
import io.airbyte.api.model.generated.SourceDefinitionRead;
import io.airbyte.api.model.generated.SourceDefinitionRead.SourceTypeEnum;
import io.airbyte.api.model.generated.SourceDefinitionReadList;
import io.airbyte.api.model.generated.SourceDefinitionUpdate;
import io.airbyte.api.model.generated.SourceRead;
import io.airbyte.api.model.generated.WorkspaceIdRequestBody;
import io.airbyte.commons.docker.DockerUtils;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.commons.util.MoreLists;
import io.airbyte.commons.version.AirbyteProtocolVersion;
import io.airbyte.commons.version.AirbyteProtocolVersionRange;
import io.airbyte.commons.version.Version;
import io.airbyte.config.ActorDefinitionResourceRequirements;
import io.airbyte.config.ActorType;
import io.airbyte.config.Configs;
import io.airbyte.config.EnvConfigs;
import io.airbyte.config.StandardSourceDefinition;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.protocol.models.ConnectorSpecification;
import io.airbyte.server.converters.ApiPojoConverters;
import io.airbyte.server.converters.SpecFetcher;
import io.airbyte.server.errors.IdNotFoundKnownException;
import io.airbyte.server.errors.InternalServerKnownException;
import io.airbyte.server.errors.UnsupportedProtocolVersionException;
import io.airbyte.server.scheduler.SynchronousResponse;
import io.airbyte.server.scheduler.SynchronousSchedulerClient;
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
public class SourceDefinitionsHandler {

  private final ConfigRepository configRepository;
  private final Supplier<UUID> uuidSupplier;
  private final AirbyteGithubStore githubStore;
  private final SynchronousSchedulerClient schedulerSynchronousClient;
  private final SourceHandler sourceHandler;
  private final AirbyteProtocolVersionRange protocolVersionRange;

  public SourceDefinitionsHandler(final ConfigRepository configRepository,
                                  final SynchronousSchedulerClient schedulerSynchronousClient,
                                  final SourceHandler sourceHandler) {
    this(configRepository, UUID::randomUUID, schedulerSynchronousClient, AirbyteGithubStore.production(), sourceHandler);
  }

  public SourceDefinitionsHandler(final ConfigRepository configRepository,
                                  final Supplier<UUID> uuidSupplier,
                                  final SynchronousSchedulerClient schedulerSynchronousClient,
                                  final AirbyteGithubStore githubStore,
                                  final SourceHandler sourceHandler) {
    this.configRepository = configRepository;
    this.uuidSupplier = uuidSupplier;
    this.schedulerSynchronousClient = schedulerSynchronousClient;
    this.githubStore = githubStore;
    this.sourceHandler = sourceHandler;

    // TODO inject protocol min and max once this handler is being converted to micronaut
    final Configs configs = new EnvConfigs();
    protocolVersionRange = new AirbyteProtocolVersionRange(configs.getAirbyteProtocolVersionMin(), configs.getAirbyteProtocolVersionMax());
  }

  @VisibleForTesting
  static SourceDefinitionRead buildSourceDefinitionRead(final StandardSourceDefinition standardSourceDefinition) {
    try {
      return new SourceDefinitionRead()
          .sourceDefinitionId(standardSourceDefinition.getSourceDefinitionId())
          .name(standardSourceDefinition.getName())
          .sourceType(getSourceType(standardSourceDefinition))
          .dockerRepository(standardSourceDefinition.getDockerRepository())
          .dockerImageTag(standardSourceDefinition.getDockerImageTag())
          .documentationUrl(new URI(standardSourceDefinition.getDocumentationUrl()))
          .icon(loadIcon(standardSourceDefinition.getIcon()))
          .protocolVersion(standardSourceDefinition.getProtocolVersion())
          .releaseStage(getReleaseStage(standardSourceDefinition))
          .releaseDate(getReleaseDate(standardSourceDefinition))
          .resourceRequirements(ApiPojoConverters.actorDefResourceReqsToApi(standardSourceDefinition.getResourceRequirements()));

    } catch (final URISyntaxException | NullPointerException e) {
      throw new InternalServerKnownException("Unable to process retrieved latest source definitions list", e);
    }
  }

  private static SourceTypeEnum getSourceType(final StandardSourceDefinition standardSourceDefinition) {
    if (standardSourceDefinition.getSourceType() == null) {
      return null;
    }
    return SourceTypeEnum.fromValue(standardSourceDefinition.getSourceType().value());
  }

  private static ReleaseStage getReleaseStage(final StandardSourceDefinition standardSourceDefinition) {
    if (standardSourceDefinition.getReleaseStage() == null) {
      return null;
    }
    return ReleaseStage.fromValue(standardSourceDefinition.getReleaseStage().value());
  }

  private static LocalDate getReleaseDate(final StandardSourceDefinition standardSourceDefinition) {
    if (standardSourceDefinition.getReleaseDate() == null || standardSourceDefinition.getReleaseDate().isBlank()) {
      return null;
    }

    return LocalDate.parse(standardSourceDefinition.getReleaseDate());
  }

  public SourceDefinitionReadList listSourceDefinitions() throws IOException, JsonValidationException {
    return toSourceDefinitionReadList(configRepository.listStandardSourceDefinitions(false));
  }

  private static SourceDefinitionReadList toSourceDefinitionReadList(final List<StandardSourceDefinition> defs) {
    final List<SourceDefinitionRead> reads = defs.stream()
        .map(SourceDefinitionsHandler::buildSourceDefinitionRead)
        .collect(Collectors.toList());
    return new SourceDefinitionReadList().sourceDefinitions(reads);
  }

  public SourceDefinitionReadList listLatestSourceDefinitions() {
    return toSourceDefinitionReadList(getLatestSources());
  }

  private List<StandardSourceDefinition> getLatestSources() {
    try {
      return githubStore.getLatestSources();
    } catch (final InterruptedException e) {
      throw new InternalServerKnownException("Request to retrieve latest destination definitions failed", e);
    }
  }

  public SourceDefinitionReadList listSourceDefinitionsForWorkspace(final WorkspaceIdRequestBody workspaceIdRequestBody)
      throws IOException {
    return toSourceDefinitionReadList(MoreLists.concat(
        configRepository.listPublicSourceDefinitions(false),
        configRepository.listGrantedSourceDefinitions(workspaceIdRequestBody.getWorkspaceId(), false)));
  }

  public PrivateSourceDefinitionReadList listPrivateSourceDefinitions(final WorkspaceIdRequestBody workspaceIdRequestBody)
      throws IOException {
    final List<Entry<StandardSourceDefinition, Boolean>> standardSourceDefinitionBooleanMap =
        configRepository.listGrantableSourceDefinitions(workspaceIdRequestBody.getWorkspaceId(), false);
    return toPrivateSourceDefinitionReadList(standardSourceDefinitionBooleanMap);
  }

  private static PrivateSourceDefinitionReadList toPrivateSourceDefinitionReadList(final List<Entry<StandardSourceDefinition, Boolean>> defs) {
    final List<PrivateSourceDefinitionRead> reads = defs.stream()
        .map(entry -> new PrivateSourceDefinitionRead()
            .sourceDefinition(buildSourceDefinitionRead(entry.getKey()))
            .granted(entry.getValue()))
        .collect(Collectors.toList());
    return new PrivateSourceDefinitionReadList().sourceDefinitions(reads);
  }

  public SourceDefinitionRead getSourceDefinition(final SourceDefinitionIdRequestBody sourceDefinitionIdRequestBody)
      throws ConfigNotFoundException, IOException, JsonValidationException {
    return buildSourceDefinitionRead(configRepository.getStandardSourceDefinition(sourceDefinitionIdRequestBody.getSourceDefinitionId()));
  }

  public SourceDefinitionRead getSourceDefinitionForWorkspace(final SourceDefinitionIdWithWorkspaceId sourceDefinitionIdWithWorkspaceId)
      throws ConfigNotFoundException, IOException, JsonValidationException {
    final UUID definitionId = sourceDefinitionIdWithWorkspaceId.getSourceDefinitionId();
    final UUID workspaceId = sourceDefinitionIdWithWorkspaceId.getWorkspaceId();
    if (!configRepository.workspaceCanUseDefinition(definitionId, workspaceId)) {
      throw new IdNotFoundKnownException("Cannot find the requested definition with given id for this workspace", definitionId.toString());
    }
    return getSourceDefinition(new SourceDefinitionIdRequestBody().sourceDefinitionId(definitionId));
  }

  public SourceDefinitionRead createPrivateSourceDefinition(final SourceDefinitionCreate sourceDefinitionCreate)
      throws JsonValidationException, IOException {
    final StandardSourceDefinition sourceDefinition = sourceDefinitionFromCreate(sourceDefinitionCreate)
        .withPublic(false)
        .withCustom(false);
    if (!protocolVersionRange.isSupported(new Version(sourceDefinition.getProtocolVersion()))) {
      throw new UnsupportedProtocolVersionException(sourceDefinition.getProtocolVersion(), protocolVersionRange.min(), protocolVersionRange.max());
    }
    configRepository.writeStandardSourceDefinition(sourceDefinition);

    return buildSourceDefinitionRead(sourceDefinition);
  }

  public SourceDefinitionRead createCustomSourceDefinition(final CustomSourceDefinitionCreate customSourceDefinitionCreate)
      throws IOException {
    final StandardSourceDefinition sourceDefinition = sourceDefinitionFromCreate(customSourceDefinitionCreate.getSourceDefinition())
        .withPublic(false)
        .withCustom(true);
    if (!protocolVersionRange.isSupported(new Version(sourceDefinition.getProtocolVersion()))) {
      throw new UnsupportedProtocolVersionException(sourceDefinition.getProtocolVersion(), protocolVersionRange.min(), protocolVersionRange.max());
    }
    configRepository.writeCustomSourceDefinition(sourceDefinition, customSourceDefinitionCreate.getWorkspaceId());

    return buildSourceDefinitionRead(sourceDefinition);
  }

  private StandardSourceDefinition sourceDefinitionFromCreate(final SourceDefinitionCreate sourceDefinitionCreate)
      throws IOException {
    final ConnectorSpecification spec = getSpecForImage(sourceDefinitionCreate.getDockerRepository(), sourceDefinitionCreate.getDockerImageTag());

    final Version airbyteProtocolVersion = AirbyteProtocolVersion.getWithDefault(spec.getProtocolVersion());

    final UUID id = uuidSupplier.get();
    return new StandardSourceDefinition()
        .withSourceDefinitionId(id)
        .withDockerRepository(sourceDefinitionCreate.getDockerRepository())
        .withDockerImageTag(sourceDefinitionCreate.getDockerImageTag())
        .withDocumentationUrl(sourceDefinitionCreate.getDocumentationUrl().toString())
        .withName(sourceDefinitionCreate.getName())
        .withIcon(sourceDefinitionCreate.getIcon())
        .withSpec(spec)
        .withProtocolVersion(airbyteProtocolVersion.serialize())
        .withTombstone(false)
        .withReleaseStage(StandardSourceDefinition.ReleaseStage.CUSTOM)
        .withResourceRequirements(ApiPojoConverters.actorDefResourceReqsToInternal(sourceDefinitionCreate.getResourceRequirements()));
  }

  public SourceDefinitionRead updateSourceDefinition(final SourceDefinitionUpdate sourceDefinitionUpdate)
      throws ConfigNotFoundException, IOException, JsonValidationException {
    final StandardSourceDefinition currentSourceDefinition =
        configRepository.getStandardSourceDefinition(sourceDefinitionUpdate.getSourceDefinitionId());

    // specs are re-fetched from the container if the image tag has changed, or if the tag is "dev",
    // to allow for easier iteration of dev images
    final boolean specNeedsUpdate = !currentSourceDefinition.getDockerImageTag().equals(sourceDefinitionUpdate.getDockerImageTag())
        || sourceDefinitionUpdate.getDockerImageTag().equals(DEV_IMAGE_TAG);
    final ConnectorSpecification spec = specNeedsUpdate
        ? getSpecForImage(currentSourceDefinition.getDockerRepository(), sourceDefinitionUpdate.getDockerImageTag())
        : currentSourceDefinition.getSpec();
    final ActorDefinitionResourceRequirements updatedResourceReqs = sourceDefinitionUpdate.getResourceRequirements() != null
        ? ApiPojoConverters.actorDefResourceReqsToInternal(sourceDefinitionUpdate.getResourceRequirements())
        : currentSourceDefinition.getResourceRequirements();

    final Version airbyteProtocolVersion = AirbyteProtocolVersion.getWithDefault(spec.getProtocolVersion());
    if (!protocolVersionRange.isSupported(airbyteProtocolVersion)) {
      throw new UnsupportedProtocolVersionException(airbyteProtocolVersion, protocolVersionRange.min(), protocolVersionRange.max());
    }

    final StandardSourceDefinition newSource = new StandardSourceDefinition()
        .withSourceDefinitionId(currentSourceDefinition.getSourceDefinitionId())
        .withDockerImageTag(sourceDefinitionUpdate.getDockerImageTag())
        .withDockerRepository(currentSourceDefinition.getDockerRepository())
        .withDocumentationUrl(currentSourceDefinition.getDocumentationUrl())
        .withName(currentSourceDefinition.getName())
        .withIcon(currentSourceDefinition.getIcon())
        .withSpec(spec)
        .withProtocolVersion(airbyteProtocolVersion.serialize())
        .withTombstone(currentSourceDefinition.getTombstone())
        .withPublic(currentSourceDefinition.getPublic())
        .withCustom(currentSourceDefinition.getCustom())
        .withReleaseStage(currentSourceDefinition.getReleaseStage())
        .withReleaseDate(currentSourceDefinition.getReleaseDate())
        .withResourceRequirements(updatedResourceReqs);

    configRepository.writeStandardSourceDefinition(newSource);
    configRepository.clearUnsupportedProtocolVersionFlag(newSource.getSourceDefinitionId(), ActorType.SOURCE, protocolVersionRange);

    return buildSourceDefinitionRead(newSource);
  }

  public SourceDefinitionRead updateCustomSourceDefinition(final CustomSourceDefinitionUpdate customSourceDefinitionUpdate)
      throws IOException, JsonValidationException, ConfigNotFoundException {
    final UUID definitionId = customSourceDefinitionUpdate.getSourceDefinition().getSourceDefinitionId();
    final UUID workspaceId = customSourceDefinitionUpdate.getWorkspaceId();
    if (!configRepository.workspaceCanUseCustomDefinition(definitionId, workspaceId)) {
      throw new IdNotFoundKnownException("Cannot find the requested definition with given id for this workspace", definitionId.toString());
    }
    return updateSourceDefinition(customSourceDefinitionUpdate.getSourceDefinition());
  }

  public void deleteSourceDefinition(final SourceDefinitionIdRequestBody sourceDefinitionIdRequestBody)
      throws JsonValidationException, IOException, ConfigNotFoundException {
    // "delete" all sources associated with the source definition as well. This will cascade to
    // connections that depend on any deleted sources.
    // Delete sources first in case a failure occurs mid-operation.

    final StandardSourceDefinition persistedSourceDefinition =
        configRepository.getStandardSourceDefinition(sourceDefinitionIdRequestBody.getSourceDefinitionId());

    for (final SourceRead sourceRead : sourceHandler.listSourcesForSourceDefinition(sourceDefinitionIdRequestBody).getSources()) {
      sourceHandler.deleteSource(sourceRead);
    }

    persistedSourceDefinition.withTombstone(true);
    configRepository.writeStandardSourceDefinition(persistedSourceDefinition);
  }

  public void deleteCustomSourceDefinition(final SourceDefinitionIdWithWorkspaceId sourceDefinitionIdWithWorkspaceId)
      throws IOException, JsonValidationException, ConfigNotFoundException {
    final UUID definitionId = sourceDefinitionIdWithWorkspaceId.getSourceDefinitionId();
    final UUID workspaceId = sourceDefinitionIdWithWorkspaceId.getWorkspaceId();
    if (!configRepository.workspaceCanUseCustomDefinition(definitionId, workspaceId)) {
      throw new IdNotFoundKnownException("Cannot find the requested definition with given id for this workspace", definitionId.toString());
    }
    deleteSourceDefinition(new SourceDefinitionIdRequestBody().sourceDefinitionId(definitionId));
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

  public PrivateSourceDefinitionRead grantSourceDefinitionToWorkspace(
                                                                      final SourceDefinitionIdWithWorkspaceId sourceDefinitionIdWithWorkspaceId)
      throws JsonValidationException, ConfigNotFoundException, IOException {
    final StandardSourceDefinition standardSourceDefinition =
        configRepository.getStandardSourceDefinition(sourceDefinitionIdWithWorkspaceId.getSourceDefinitionId());
    configRepository.writeActorDefinitionWorkspaceGrant(
        sourceDefinitionIdWithWorkspaceId.getSourceDefinitionId(),
        sourceDefinitionIdWithWorkspaceId.getWorkspaceId());
    return new PrivateSourceDefinitionRead()
        .sourceDefinition(buildSourceDefinitionRead(standardSourceDefinition))
        .granted(true);
  }

  public void revokeSourceDefinitionFromWorkspace(final SourceDefinitionIdWithWorkspaceId sourceDefinitionIdWithWorkspaceId)
      throws IOException {
    configRepository.deleteActorDefinitionWorkspaceGrant(
        sourceDefinitionIdWithWorkspaceId.getSourceDefinitionId(),
        sourceDefinitionIdWithWorkspaceId.getWorkspaceId());
  }

}
