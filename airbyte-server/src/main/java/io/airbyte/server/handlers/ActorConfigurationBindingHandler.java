/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.handlers;

import io.airbyte.api.model.ActorConfigurationBindingCreate;
import io.airbyte.config.ActorConfigurationBinding;
import io.airbyte.config.persistence.SecretsRepositoryWriter;
import io.airbyte.validation.json.JsonValidationException;
import java.io.IOException;

public class ActorConfigurationBindingHandler {

  private final SecretsRepositoryWriter secretsRepositoryWriter;

  public ActorConfigurationBindingHandler(final SecretsRepositoryWriter secretsRepositoryWriter) {
    this.secretsRepositoryWriter = secretsRepositoryWriter;
  }

  public void createActorConfigurationBinding(final ActorConfigurationBindingCreate actorConfigurationBindingCreate)
      throws JsonValidationException, IOException {
    final ActorConfigurationBinding actorConfigurationBinding = new ActorConfigurationBinding().withActorDefinitionId(
        actorConfigurationBindingCreate.getActorDefinitionId()).withConfiguration(actorConfigurationBindingCreate.getConfiguration());

    secretsRepositoryWriter.writeActorConfigurationBinding(actorConfigurationBinding);
  }

}
