/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.handlers;

import io.airbyte.api.model.DestinationDefinitionCreate;
import io.airbyte.api.model.DestinationDefinitionIdRequestBody;
import io.airbyte.api.model.DestinationDefinitionRead;
import io.airbyte.api.model.DestinationDefinitionReadList;
import io.airbyte.api.model.DestinationDefinitionUpdate;
import io.airbyte.api.model.DestinationRead;
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

public class DestinationDefinitionsHandler2 extends
    ActorDefinitionsHandler<DestinationDefinitionRead, DestinationDefinitionReadList, DestinationDefinitionCreate, DestinationDefinitionUpdate, DestinationDefinitionIdRequestBody> {

  private final DestinationHandler destinationHandler;

  public DestinationDefinitionsHandler2(final ConfigRepository configRepository,
                                        final SynchronousSchedulerClient schedulerSynchronousClient,
                                        final DestinationHandler destinationHandler) {
    this(configRepository, UUID::randomUUID, schedulerSynchronousClient, AirbyteGithubStore.production(), destinationHandler);
  }

  public DestinationDefinitionsHandler2(final ConfigRepository configRepository,
                                        final Supplier<UUID> uuidSupplier,
                                        final SynchronousSchedulerClient schedulerSynchronousClient,
                                        final AirbyteGithubStore githubStore,
                                        final DestinationHandler destinationHandler) {
    super(configRepository,
        uuidSupplier,
        schedulerSynchronousClient,
        githubStore,
        ActorType.DESTINATION);
    this.destinationHandler = destinationHandler;
  }

  @Override
  DestinationDefinitionRead toRead(final ActorDefinition actorDefinition) {
    return new DestinationDefinitionRead()
        .destinationDefinitionId(actorDefinition.getId())
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
  DestinationDefinitionReadList toList(final List<DestinationDefinitionRead> reads) {
    return new DestinationDefinitionReadList().destinationDefinitions(reads);
  }

  @Override
  ActorDefinition fromCreate(final DestinationDefinitionCreate create) {
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
  ActorDefinition fromUpdate(final DestinationDefinitionUpdate update) {
    return new ActorDefinition()
        .withActorType(actorType)
        .withId(update.getDestinationDefinitionId())
        .withDockerImageTag(update.getDockerImageTag())
        .withResourceRequirements(ApiPojoConverters.actorDefResourceReqsToInternal(update.getResourceRequirements()));
  }

  @Override
  UUID fromId(final DestinationDefinitionIdRequestBody idRequest) {
    return idRequest.getDestinationDefinitionId();
  }

  @Override
  void deleteChildren(final UUID definitionId) throws JsonValidationException, ConfigNotFoundException, IOException {
    final DestinationDefinitionIdRequestBody destDefRequest = new DestinationDefinitionIdRequestBody().destinationDefinitionId(definitionId);
    for (final DestinationRead destinationRead : destinationHandler.listDestinationsForDestinationDefinition(destDefRequest).getDestinations()) {
      destinationHandler.deleteDestination(destinationRead);
    }
  }

}
