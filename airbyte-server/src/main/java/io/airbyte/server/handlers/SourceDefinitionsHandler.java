/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.handlers;

import io.airbyte.api.model.SourceDefinitionCreate;
import io.airbyte.api.model.SourceDefinitionIdRequestBody;
import io.airbyte.api.model.SourceDefinitionRead;
import io.airbyte.api.model.SourceDefinitionReadList;
import io.airbyte.api.model.SourceDefinitionUpdate;
import io.airbyte.api.model.SourceRead;
import io.airbyte.config.ActorDefinition;
import io.airbyte.config.ActorDefinition.ActorDefinitionReleaseStage;
import io.airbyte.config.ActorDefinition.ActorType;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.scheduler.client.SynchronousSchedulerClient;
import io.airbyte.server.converters.ApiPojoConverters;
import io.airbyte.server.services.AirbyteGithubStore;
import io.airbyte.validation.json.JsonValidationException;
import java.io.IOException;
import java.util.List;
import java.util.UUID;
import java.util.function.Supplier;

public class SourceDefinitionsHandler extends
    ActorDefinitionsHandler<SourceDefinitionRead, SourceDefinitionReadList, SourceDefinitionCreate, SourceDefinitionUpdate, SourceDefinitionIdRequestBody> {

  private final SourceHandler sourceHandler;

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
    super(configRepository,
        uuidSupplier,
        schedulerSynchronousClient,
        githubStore,
        ActorType.SOURCE);
    this.sourceHandler = sourceHandler;
  }

  @Override
  SourceDefinitionRead toRead(final ActorDefinition actorDefinition) {
    return new SourceDefinitionRead()
        .sourceDefinitionId(actorDefinition.getId())
        .name(actorDefinition.getName())
        .dockerRepository(actorDefinition.getDockerRepository())
        .dockerImageTag(actorDefinition.getDockerImageTag())
        .documentationUrl(getDocumentUri(actorDefinition.getDocumentationUrl()))
        .icon(loadIcon(actorDefinition.getIcon()))
        .releaseStage(getReleaseStage(actorDefinition))
        .releaseDate(getReleaseDate(actorDefinition))
        .resourceRequirements(ApiPojoConverters.actorDefResourceReqsToApi(actorDefinition.getResourceRequirements()));
  }

  @Override
  SourceDefinitionReadList toList(final List<SourceDefinitionRead> reads) {
    return new SourceDefinitionReadList().sourceDefinitions(reads);
  }

  @Override
  ActorDefinition fromCreate(final SourceDefinitionCreate create) {
    return new ActorDefinition()
        .withActorType(actorType)
        .withId(null) // will get populated internally.
        .withDockerRepository(create.getDockerRepository())
        .withDockerImageTag(create.getDockerImageTag())
        .withDocumentationUrl(create.getDocumentationUrl().toString())
        .withName(create.getName())
        .withIcon(create.getIcon())
        .withSpec(null) // will get populated internally.
        .withTombstone(false)
        .withReleaseStage(ActorDefinitionReleaseStage.CUSTOM)
        .withResourceRequirements(ApiPojoConverters.actorDefResourceReqsToInternal(create.getResourceRequirements()));
  }

  @Override
  ActorDefinition fromUpdate(final SourceDefinitionUpdate update) {
    return new ActorDefinition()
        .withActorType(actorType)
        .withId(update.getSourceDefinitionId())
        .withDockerImageTag(update.getDockerImageTag())
        .withResourceRequirements(ApiPojoConverters.actorDefResourceReqsToInternal(update.getResourceRequirements()));
  }

  @Override
  UUID fromId(final SourceDefinitionIdRequestBody idRequest) {
    return idRequest.getSourceDefinitionId();
  }

  @Override
  void deleteChildren(final UUID definitionId) throws JsonValidationException, ConfigNotFoundException, IOException {
    final SourceDefinitionIdRequestBody destDefRequest = new SourceDefinitionIdRequestBody().sourceDefinitionId(definitionId);
    for (final SourceRead sourceRead : sourceHandler.listSourcesForSourceDefinition(destDefRequest).getSources()) {
      sourceHandler.deleteSource(sourceRead);
    }
  }

}
