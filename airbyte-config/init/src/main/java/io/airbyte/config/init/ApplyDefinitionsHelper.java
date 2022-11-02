/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config.init;

import io.airbyte.config.StandardDestinationDefinition;
import io.airbyte.config.StandardSourceDefinition;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.validation.json.JsonValidationException;
import java.io.IOException;
import java.util.List;

/**
 * Helper class used to apply actor definitions from a DefinitionsProvider to the database. This is
 * here to enable easy reuse of definition application logic in bootloader and cron.
 */
public class ApplyDefinitionsHelper {

  private final ConfigRepository configRepository;
  private final DefinitionsProvider definitionsProvider;

  public ApplyDefinitionsHelper(final ConfigRepository configRepository, final DefinitionsProvider definitionsProvider) {
    this.configRepository = configRepository;
    this.definitionsProvider = definitionsProvider;
  }

  public void apply() throws JsonValidationException, IOException {
    apply(false);
  }

  /**
   * Apply the latest definitions from the provider to the repository.
   *
   * @param updateAll - Whether we should overwrite all stored definitions
   */
  public void apply(final boolean updateAll) throws JsonValidationException, IOException {
    if (updateAll) {
      final List<StandardSourceDefinition> latestSourceDefinitions = definitionsProvider.getSourceDefinitions();
      for (final StandardSourceDefinition def : latestSourceDefinitions) {
        configRepository.writeStandardSourceDefinition(def);
      }

      final List<StandardDestinationDefinition> latestDestinationDefinitions = definitionsProvider.getDestinationDefinitions();
      for (final StandardDestinationDefinition def : latestDestinationDefinitions) {
        configRepository.writeStandardDestinationDefinition(def);
      }
    } else {
      // todo (pedroslopez): Logic to apply definitions should be moved outside of the
      // DatabaseConfigPersistence class and behavior standardized
      configRepository.seedActorDefinitions(
          definitionsProvider.getSourceDefinitions(),
          definitionsProvider.getDestinationDefinitions());
    }
  }

}
