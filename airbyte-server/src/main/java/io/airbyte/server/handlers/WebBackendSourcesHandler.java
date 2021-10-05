/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.handlers;

import io.airbyte.analytics.TrackingClient;
import io.airbyte.api.model.SourceCreate;
import io.airbyte.api.model.SourceRead;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.scheduler.persistence.job_factory.OAuthConfigSupplier;
import io.airbyte.validation.json.JsonValidationException;
import java.io.IOException;

public class WebBackendSourcesHandler {

  private final SourceHandler sourceHandler;
  private final OAuthConfigSupplier oAuthConfigSupplier;

  public WebBackendSourcesHandler(SourceHandler sourceHandler, ConfigRepository configRepository, TrackingClient trackingClient) {
    this.sourceHandler = sourceHandler;
    oAuthConfigSupplier = new OAuthConfigSupplier(configRepository, true, trackingClient);
  }

  public SourceRead webBackendCreateSource(SourceCreate sourceCreate) throws JsonValidationException, ConfigNotFoundException, IOException {
    sourceCreate.connectionConfiguration(
        oAuthConfigSupplier.injectSourceOAuthParameters(
            sourceCreate.getSourceDefinitionId(),
            sourceCreate.getWorkspaceId(),
            sourceCreate.getConnectionConfiguration()));
    return sourceHandler.createSource(sourceCreate);
  }

}
