/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config.init;

import io.airbyte.commons.version.AirbyteProtocolVersion;
import io.airbyte.commons.version.AirbyteProtocolVersionRange;
import io.airbyte.config.StandardDestinationDefinition;
import io.airbyte.config.StandardSourceDefinition;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.persistence.job.JobPersistence;
import io.airbyte.validation.json.JsonValidationException;
import io.micronaut.context.annotation.Requires;
import jakarta.inject.Singleton;
import java.io.IOException;
import java.util.List;
import java.util.Optional;
import lombok.extern.slf4j.Slf4j;

/**
 * Helper class used to apply actor definitions from a DefinitionsProvider to the database. This is
 * here to enable easy reuse of definition application logic in bootloader and cron.
 */
@Singleton
@Requires(bean = ConfigRepository.class)
@Requires(bean = JobPersistence.class)
@Slf4j
public class ApplyDefinitionsHelper {

  private final ConfigRepository configRepository;
  private final Optional<DefinitionsProvider> definitionsProviderOptional;
  private final JobPersistence jobPersistence;

  public ApplyDefinitionsHelper(final ConfigRepository configRepository,
                                final Optional<DefinitionsProvider> definitionsProviderOptional,
                                final JobPersistence jobPersistence) {
    this.configRepository = configRepository;
    this.definitionsProviderOptional = definitionsProviderOptional;
    this.jobPersistence = jobPersistence;
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
    if (definitionsProviderOptional.isPresent()) {
      final DefinitionsProvider definitionsProvider = definitionsProviderOptional.get();
      final Optional<AirbyteProtocolVersionRange> currentProtocolRange = getCurrentProtocolRange();

      if (updateAll) {
        final List<StandardSourceDefinition> latestSourceDefinitions = definitionsProvider.getSourceDefinitions();
        for (final StandardSourceDefinition def : filterStandardSourceDefinitions(currentProtocolRange, latestSourceDefinitions)) {
          configRepository.writeStandardSourceDefinition(def);
        }

        final List<StandardDestinationDefinition> latestDestinationDefinitions = definitionsProvider.getDestinationDefinitions();
        for (final StandardDestinationDefinition def : filterStandardDestinationDefinitions(currentProtocolRange, latestDestinationDefinitions)) {
          configRepository.writeStandardDestinationDefinition(def);
        }
      } else {
        // todo (pedroslopez): Logic to apply definitions should be moved outside of the
        // DatabaseConfigPersistence class and behavior standardized
        configRepository.seedActorDefinitions(
            filterStandardSourceDefinitions(currentProtocolRange, definitionsProvider.getSourceDefinitions()),
            filterStandardDestinationDefinitions(currentProtocolRange, definitionsProvider.getDestinationDefinitions()));
      }
    } else {
      log.warn("Skipping application of latest definitions.  Definitions provider not configured.");
    }
  }

  private List<StandardDestinationDefinition> filterStandardDestinationDefinitions(final Optional<AirbyteProtocolVersionRange> protocolVersionRange,
                                                                                   final List<StandardDestinationDefinition> destDefs) {
    if (protocolVersionRange.isEmpty()) {
      return destDefs;
    }

    return destDefs.stream().filter(def -> {
      final boolean isSupported = isProtocolVersionSupported(protocolVersionRange.get(), def.getSpec().getProtocolVersion());
      if (!isSupported) {
        log.warn("Destination {} {} has an incompatible protocol version ({})... ignoring.",
            def.getDestinationDefinitionId(), def.getName(), def.getSpec().getProtocolVersion());
      }
      return isSupported;
    }).toList();
  }

  private List<StandardSourceDefinition> filterStandardSourceDefinitions(final Optional<AirbyteProtocolVersionRange> protocolVersionRange,
                                                                         final List<StandardSourceDefinition> sourceDefs) {
    if (protocolVersionRange.isEmpty()) {
      return sourceDefs;
    }

    return sourceDefs.stream().filter(def -> {
      final boolean isSupported = isProtocolVersionSupported(protocolVersionRange.get(), def.getSpec().getProtocolVersion());
      if (!isSupported) {
        log.warn("Source {} {} has an incompatible protocol version ({})... ignoring.",
            def.getSourceDefinitionId(), def.getName(), def.getSpec().getProtocolVersion());
      }
      return isSupported;
    }).toList();
  }

  private boolean isProtocolVersionSupported(final AirbyteProtocolVersionRange protocolVersionRange, final String protocolVersion) {
    return protocolVersionRange.isSupported(AirbyteProtocolVersion.getWithDefault(protocolVersion));
  }

  private Optional<AirbyteProtocolVersionRange> getCurrentProtocolRange() throws IOException {
    if (jobPersistence == null) {
      // TODO Remove this once cloud has been migrated and job persistence is always defined
      return Optional.empty();
    }

    return jobPersistence.getCurrentProtocolVersionRange();
  }

}
