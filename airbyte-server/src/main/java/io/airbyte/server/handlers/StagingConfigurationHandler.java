/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.handlers;

import io.airbyte.api.model.StagingConfigurationCreate;
import io.airbyte.api.model.StagingConfigurationRead;
import io.airbyte.config.StagingConfiguration;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.validation.json.JsonValidationException;
import java.io.IOException;

public class StagingConfigurationHandler {

  private final ConfigRepository configRepository;

  public StagingConfigurationHandler(final ConfigRepository configRepository) {
    this.configRepository = configRepository;
  }

  public StagingConfigurationRead createStagingConfiguration(final StagingConfigurationCreate stagingConfigurationCreate)
      throws JsonValidationException, IOException {
    final StagingConfiguration stagingConfiguration = new StagingConfiguration().withDestinationDefinitionId(
        stagingConfigurationCreate.getDestinationDefinitionId()).withConfiguration(stagingConfigurationCreate.getStagingConfiguration());

    configRepository.writeStagingConfiguration(stagingConfiguration);

    return new StagingConfigurationRead().destinationDefinitionId(stagingConfiguration.getDestinationDefinitionId());
  }

}
