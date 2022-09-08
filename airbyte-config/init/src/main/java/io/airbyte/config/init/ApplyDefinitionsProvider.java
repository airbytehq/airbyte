/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config.init;

import io.airbyte.config.StandardDestinationDefinition;
import io.airbyte.config.StandardSourceDefinition;
import io.airbyte.config.persistence.ConfigPersistence;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.validation.json.JsonValidationException;
import java.io.IOException;
import java.util.List;

// TODO naming
public class ApplyDefinitionsProvider {

  private final ConfigRepository configRepository;
  private final DefinitionsProvider definitionsProvider;

  public ApplyDefinitionsProvider(final ConfigRepository configRepository, final DefinitionsProvider definitionsProvider) {
    this.configRepository = configRepository;
    this.definitionsProvider = definitionsProvider;
  }

  public void apply() throws JsonValidationException, IOException {
    apply(false);
  }

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
      // todo This should be updated to move the logic to apply definition updates outside of the
      // DatabaseConfigPersistence class
      final ConfigPersistence dbConfigPersistence = configRepository.getConfigPersistence();
      final ConfigPersistence providerConfigPersistence = new DefinitionProviderToConfigPersistenceAdapter(definitionsProvider);
      dbConfigPersistence.loadData(providerConfigPersistence);
    }
  }

}
