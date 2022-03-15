/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.handlers;

import io.airbyte.api.model.StagingConfigurationCreate;
import io.airbyte.api.model.StagingConfigurationRead;
import io.airbyte.config.StagingConfiguration;
import io.airbyte.config.persistence.SecretsRepositoryWriter;
import io.airbyte.validation.json.JsonValidationException;
import java.io.IOException;

public class StagingConfigurationHandler {

  private final SecretsRepositoryWriter secretsRepositoryWriter;

  public StagingConfigurationHandler(final SecretsRepositoryWriter secretsRepositoryWriter) {
    this.secretsRepositoryWriter = secretsRepositoryWriter;
  }

  public StagingConfigurationRead createStagingConfiguration(final StagingConfigurationCreate stagingConfigurationCreate)
      throws JsonValidationException, IOException {
    final StagingConfiguration stagingConfiguration = new StagingConfiguration().withDestinationDefinitionId(
        stagingConfigurationCreate.getDestinationDefinitionId()).withConfiguration(stagingConfigurationCreate.getStagingConfiguration());

    secretsRepositoryWriter.writeStagingConfiguration(stagingConfiguration);

    return new StagingConfigurationRead().destinationDefinitionId(stagingConfiguration.getDestinationDefinitionId());
  }

}
