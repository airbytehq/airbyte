/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.server.handlers;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.google.common.annotations.VisibleForTesting;
import io.airbyte.api.model.generated.ConnectorBuilderProjectIdWithWorkspaceId;
import io.airbyte.api.model.generated.ConnectorBuilderProjectWithWorkspaceId;
import io.airbyte.api.model.generated.CustomSourceDefinitionCreate;
import io.airbyte.api.model.generated.ExistingConnectorBuilderProjectWithWorkspaceId;
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
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.commons.server.ServerConstants;
import io.airbyte.commons.server.converters.ApiPojoConverters;
import io.airbyte.commons.server.converters.SpecFetcher;
import io.airbyte.commons.server.errors.IdNotFoundKnownException;
import io.airbyte.commons.server.errors.InternalServerKnownException;
import io.airbyte.commons.server.errors.UnsupportedProtocolVersionException;
import io.airbyte.commons.server.scheduler.SynchronousResponse;
import io.airbyte.commons.server.scheduler.SynchronousSchedulerClient;
import io.airbyte.commons.server.services.AirbyteGithubStore;
import io.airbyte.commons.util.MoreLists;
import io.airbyte.commons.version.AirbyteProtocolVersion;
import io.airbyte.commons.version.AirbyteProtocolVersionRange;
import io.airbyte.commons.version.Version;
import io.airbyte.config.ActorDefinitionResourceRequirements;
import io.airbyte.config.ActorType;
import io.airbyte.config.Configs;
import io.airbyte.config.ConnectorBuilderProject;
import io.airbyte.config.EnvConfigs;
import io.airbyte.config.StandardSourceDefinition;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.protocol.models.ConnectorSpecification;
import io.airbyte.validation.json.JsonValidationException;
import jakarta.inject.Inject;
import jakarta.inject.Singleton;
import java.io.IOException;
import java.net.URI;
import java.net.URISyntaxException;
import java.time.LocalDate;
import java.util.List;
import java.util.Map.Entry;
import java.util.Optional;
import java.util.UUID;
import java.util.function.Supplier;
import java.util.stream.Collectors;

@SuppressWarnings("PMD.AvoidCatchingNPE")
@Singleton
public class ConnectorBuilderProjectsHandler {

  private final ConfigRepository configRepository;
  private final Supplier<UUID> uuidSupplier;

  @Inject
  public ConnectorBuilderProjectsHandler(final ConfigRepository configRepository,
                                  final Supplier<UUID> uuidSupplier) {
    this.configRepository = configRepository;
    this.uuidSupplier = uuidSupplier;
  }

  // This should be deleted when cloud is migrated to micronaut
  @Deprecated(forRemoval = true)
  public ConnectorBuilderProjectsHandler(final ConfigRepository configRepository,
                                  final SourceHandler sourceHandler) {
    this.configRepository = configRepository;
    this.uuidSupplier = UUID::randomUUID;
  }

  private ConnectorBuilderProject builderProjectFromUpdate(final ExistingConnectorBuilderProjectWithWorkspaceId projectCreate) {
    return new ConnectorBuilderProject().
        withBuilderProjectId(projectCreate.getBuilderProjectId()).
        withWorkspaceId(projectCreate.getWorkspaceId()).
        withName(projectCreate.getBuilderProject().getName()).
        withManifestDraft(new ObjectMapper().valueToTree(projectCreate.getBuilderProject().getDraftManifest()));
  }

  private ConnectorBuilderProject builderProjectFromCreate(final ConnectorBuilderProjectWithWorkspaceId projectCreate) {
    final UUID id = uuidSupplier.get();

    return new ConnectorBuilderProject().
        withBuilderProjectId(id).
        withWorkspaceId(projectCreate.getWorkspaceId()).
        withName(projectCreate.getBuilderProject().getName()).
        withManifestDraft(new ObjectMapper().valueToTree(projectCreate.getBuilderProject().getDraftManifest()));
  }

  private ConnectorBuilderProjectIdWithWorkspaceId idResponseFromBuilderProject(final ConnectorBuilderProject project) {
    return new ConnectorBuilderProjectIdWithWorkspaceId().workspaceId(project.getWorkspaceId()).builderProjectId(project.getBuilderProjectId());
  }

  public ConnectorBuilderProjectIdWithWorkspaceId createConnectorBuilderProject(final ConnectorBuilderProjectWithWorkspaceId projectCreate)
      throws IOException {
    final ConnectorBuilderProject project = builderProjectFromCreate(projectCreate);

    configRepository.writeBuilderProject(project);

    return idResponseFromBuilderProject(project);
  }

  public void updateConnectorBuilderProject(final ExistingConnectorBuilderProjectWithWorkspaceId projectUpdate)
      throws IOException {
    final ConnectorBuilderProject project = builderProjectFromUpdate(projectUpdate);
    final Optional<ConnectorBuilderProject> storedProject = configRepository.getConnectorBuilderProject(project.getBuilderProjectId(), project.getWorkspaceId());

    if (storedProject.isEmpty()) {
      throw new IdNotFoundKnownException("Cannot find builder project with the given id for this workspace", projectUpdate.getBuilderProjectId().toString());
    }

    configRepository.writeBuilderProject(project);
  }

  public void deleteConnectorBuilderProject(final ConnectorBuilderProjectIdWithWorkspaceId projectDelete)
      throws IOException {
    final Optional<ConnectorBuilderProject> storedProject = configRepository.getConnectorBuilderProject(projectDelete.getBuilderProjectId(), projectDelete.getWorkspaceId());

    if (storedProject.isEmpty()) {
      throw new IdNotFoundKnownException("Cannot find builder project with the given id for this workspace", projectDelete.getBuilderProjectId().toString());
    }

    configRepository.deleteBuilderProject(projectDelete.getBuilderProjectId(), projectDelete.getWorkspaceId());
  }
}
