/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.handlers;

import io.airbyte.analytics.TrackingClient;
import io.airbyte.api.model.DestinationCreate;
import io.airbyte.api.model.DestinationRead;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.scheduler.persistence.job_factory.OAuthConfigSupplier;
import io.airbyte.validation.json.JsonValidationException;
import java.io.IOException;

public class WebBackendDestinationsHandler {

  private final DestinationHandler destinationHandler;
  private final OAuthConfigSupplier oAuthConfigSupplier;

  public WebBackendDestinationsHandler(DestinationHandler destinationHandler, ConfigRepository configRepository, TrackingClient trackingClient) {
    this.destinationHandler = destinationHandler;
    oAuthConfigSupplier = new OAuthConfigSupplier(configRepository, true, trackingClient);
  }

  public DestinationRead webBackendCreateDestination(DestinationCreate destinationCreate)
      throws JsonValidationException, ConfigNotFoundException, IOException {
    destinationCreate.connectionConfiguration(
        oAuthConfigSupplier.injectDestinationOAuthParameters(
            destinationCreate.getDestinationDefinitionId(),
            destinationCreate.getWorkspaceId(),
            destinationCreate.getConnectionConfiguration()));
    return destinationHandler.createDestination(destinationCreate);
  }

}
