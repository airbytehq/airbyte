/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.handlers;

import io.airbyte.analytics.TrackingClient;
import io.airbyte.api.model.SourceCreate;
import io.airbyte.api.model.SourceRead;
import io.airbyte.commons.docker.DockerUtils;
import io.airbyte.config.StandardSourceDefinition;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.protocol.models.ConnectorSpecification;
import io.airbyte.scheduler.persistence.job_factory.OAuthConfigSupplier;
import io.airbyte.server.converters.SpecFetcher;
import io.airbyte.validation.json.JsonValidationException;
import java.io.IOException;
import java.util.UUID;

public class WebBackendSourcesHandler {

  private final SourceHandler sourceHandler;
  private final OAuthConfigSupplier oAuthConfigSupplier;
  private final ConfigRepository configRepository;
  private final SpecFetcher specFetcher;

  public WebBackendSourcesHandler(final SourceHandler sourceHandler,
                                  final ConfigRepository configRepository,
                                  final TrackingClient trackingClient,
                                  final SpecFetcher specFetcher) {
    this.sourceHandler = sourceHandler;
    this.specFetcher = specFetcher;
    this.configRepository = configRepository;
    oAuthConfigSupplier = new OAuthConfigSupplier(configRepository, true, trackingClient);
  }

  public SourceRead webBackendCreateSource(final SourceCreate sourceCreate) throws JsonValidationException, ConfigNotFoundException, IOException {
    sourceCreate.connectionConfiguration(
        oAuthConfigSupplier.injectSourceOAuthParameters(
            sourceCreate.getSourceDefinitionId(),
            sourceCreate.getWorkspaceId(),
            sourceCreate.getConnectionConfiguration(),
            getSourceConnectorSpec(sourceCreate.getSourceDefinitionId())));
    return sourceHandler.createSource(sourceCreate);
  }

  private ConnectorSpecification getSourceConnectorSpec(final UUID sourceDefId) throws JsonValidationException, ConfigNotFoundException, IOException {
    final StandardSourceDefinition sourceDef = configRepository.getStandardSourceDefinition(sourceDefId);
    final String sourceImageName = DockerUtils.getTaggedImageName(sourceDef.getDockerRepository(), sourceDef.getDockerImageTag());
    return specFetcher.execute(sourceImageName);
  }

}
