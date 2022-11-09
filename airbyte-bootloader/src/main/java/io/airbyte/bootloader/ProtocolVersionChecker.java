/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.bootloader;

import io.airbyte.commons.version.AirbyteProtocolVersion;
import io.airbyte.commons.version.AirbyteProtocolVersionRange;
import io.airbyte.commons.version.Version;
import io.airbyte.config.ActorType;
import io.airbyte.config.Configs;
import io.airbyte.config.StandardDestinationDefinition;
import io.airbyte.config.StandardSourceDefinition;
import io.airbyte.config.init.DefinitionsProvider;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.persistence.job.JobPersistence;
import java.io.IOException;
import java.util.HashSet;
import java.util.Map;
import java.util.Map.Entry;
import java.util.Optional;
import java.util.Set;
import java.util.UUID;
import java.util.stream.Collectors;
import java.util.stream.Stream;
import lombok.extern.slf4j.Slf4j;

@Slf4j
public class ProtocolVersionChecker {

  private final JobPersistence jobPersistence;
  private final Configs configs;
  private final ConfigRepository configRepository;
  private final DefinitionsProvider definitionsProvider;

  // Dependencies could be simplified once we break some pieces up:
  // * JobPersistence for accessing the airbyte_metadata table.
  // * Configs for getting the new Airbyte Protocol Range from the env vars.
  // * ConfigRepository for accessing ActorDefinitions
  public ProtocolVersionChecker(final JobPersistence jobPersistence,
                                final Configs configs,
                                final ConfigRepository configRepository,
                                final DefinitionsProvider definitionsProvider) {
    this.jobPersistence = jobPersistence;
    this.configs = configs;
    this.configRepository = configRepository;
    this.definitionsProvider = definitionsProvider;
  }

  /**
   * Validate the AirbyteProtocolVersion support range between the platform and the connectors.
   * <p>
   * The goal is to make sure that we do not end up disabling existing connections after an upgrade
   * that changes the protocol support range.
   *
   * @param supportAutoUpgrade whether the connectors will be automatically upgraded by the platform
   * @return the supported protocol version range if check is successful, Optional.empty() if we would
   *         break existing connections.
   * @throws IOException
   */
  public Optional<AirbyteProtocolVersionRange> validate(final boolean supportAutoUpgrade) throws IOException {
    final AirbyteProtocolVersionRange currentRange = getCurrentProtocolVersionRange();
    final AirbyteProtocolVersionRange targetRange = getTargetProtocolVersionRange();

    if (currentRange.equals(targetRange)) {
      log.info("Using AirbyteProtocolVersion range [{}..{}]", targetRange.min().serialize(), targetRange.max().serialize());
      return Optional.of(targetRange);
    }

    log.info("Detected an AirbyteProtocolVersion range change from [{}..{}] to [{}..{}]",
        currentRange.min().serialize(), currentRange.max().serialize(),
        targetRange.min().serialize(), targetRange.max().serialize());

    final Map<ActorType, Set<UUID>> conflicts = getConflictingActorDefinitions(targetRange);

    if (conflicts.isEmpty()) {
      log.info("No conflicts");
      return Optional.of(targetRange);
    }

    final Set<UUID> destConflicts = conflicts.getOrDefault(ActorType.DESTINATION, new HashSet<>());
    final Set<UUID> sourceConflicts = conflicts.getOrDefault(ActorType.SOURCE, new HashSet<>());

    if (!supportAutoUpgrade) {
      // If we do not support auto upgrade, any conflict of used connectors must be resolved before being
      // able to upgrade the platform.
      log.warn("The following connectors need to be upgraded before being able to upgrade the platform");
      formatActorDefinitionForLogging(destConflicts, sourceConflicts).forEach(log::warn);
      return Optional.empty();
    }

    final Set<UUID> remainingDestConflicts =
        projectRemainingConflictsAfterConnectorUpgrades(targetRange, destConflicts, ActorType.DESTINATION);
    final Set<UUID> remainingSourceConflicts =
        projectRemainingConflictsAfterConnectorUpgrades(targetRange, sourceConflicts, ActorType.SOURCE);

    if (!remainingDestConflicts.isEmpty() || !remainingSourceConflicts.isEmpty()) {
      // These set of connectors need a manual intervention because there is no compatible version listed
      formatActorDefinitionForLogging(remainingDestConflicts, remainingSourceConflicts).forEach(log::warn);
      return Optional.empty();
    }

    // These can be auto upgraded
    destConflicts.removeAll(remainingDestConflicts);
    sourceConflicts.removeAll(remainingSourceConflicts);
    log.info("The following connectors will be upgraded");
    formatActorDefinitionForLogging(destConflicts, sourceConflicts).forEach(log::info);
    return Optional.of(targetRange);
  }

  protected AirbyteProtocolVersionRange getCurrentProtocolVersionRange() throws IOException {
    Optional<Version> min = jobPersistence.getAirbyteProtocolVersionMin();
    Optional<Version> max = jobPersistence.getAirbyteProtocolVersionMax();

    if (min.isPresent() != max.isPresent()) {
      // Flagging this because this would be highly suspicious but not bad enough that we should fail
      // hard.
      // If the new config is fine, the system should self-heal.
      log.warn("Inconsistent AirbyteProtocolVersion found, only one of min/max was found. (min:{}, max:{})",
          min.map(Version::serialize).orElse(""), max.map(Version::serialize).orElse(""));
    }

    return new AirbyteProtocolVersionRange(min.orElse(AirbyteProtocolVersion.DEFAULT_AIRBYTE_PROTOCOL_VERSION),
        max.orElse(AirbyteProtocolVersion.DEFAULT_AIRBYTE_PROTOCOL_VERSION));
  }

  protected AirbyteProtocolVersionRange getTargetProtocolVersionRange() {
    return new AirbyteProtocolVersionRange(configs.getAirbyteProtocolVersionMin(), configs.getAirbyteProtocolVersionMax());
  }

  protected Map<ActorType, Set<UUID>> getConflictingActorDefinitions(final AirbyteProtocolVersionRange targetRange) throws IOException {
    final Map<UUID, Map.Entry<ActorType, Version>> actorDefIdToProtocolVersion = configRepository.getActorDefinitionToProtocolVersionMap();
    final Map<ActorType, Set<UUID>> conflicts =
        actorDefIdToProtocolVersion.entrySet().stream()
            // Keeping only ActorDefinitionIds that have an unsupported protocol version
            .filter(e -> !targetRange.isSupported(e.getValue().getValue()))
            // Build the ActorType -> List[ActorDefIds] map
            .map(e -> Map.entry(e.getValue().getKey(), e.getKey()))
            // Group by ActorType and transform the List<Entry<ActorType, UUID>> into a Set<UUID>
            .collect(Collectors.groupingBy(Entry::getKey,
                Collectors.collectingAndThen(Collectors.toList(), list -> list.stream().map(Entry::getValue).collect(Collectors.toSet()))));
    return conflicts;
  }

  protected Set<UUID> projectRemainingConflictsAfterConnectorUpgrades(final AirbyteProtocolVersionRange targetRange,
                                                                      final Set<UUID> initialConflicts,
                                                                      final ActorType actorType) {
    if (initialConflicts.isEmpty()) {
      return Set.of();
    }

    final Set<UUID> upgradedSourceDefs = getProtocolVersionsForActorDefinitions(actorType)
        // Keep definition ids if the protocol version will fall into the new supported range
        .filter(e -> initialConflicts.contains(e.getKey()) && targetRange.isSupported(e.getValue()))
        .map(Entry::getKey)
        .collect(Collectors.toSet());

    // Get the set of source definitions that will still have conflict after the connector upgrades
    final Set<UUID> remainingConflicts = new HashSet<>(initialConflicts);
    remainingConflicts.removeAll(upgradedSourceDefs);
    return remainingConflicts;
  }

  protected Stream<Entry<UUID, Version>> getProtocolVersionsForActorDefinitions(final ActorType actorType) {
    Stream<Entry<UUID, Version>> stream;
    if (actorType == ActorType.SOURCE) {
      stream = definitionsProvider.getSourceDefinitions()
          .stream()
          .map(def -> Map.entry(def.getSourceDefinitionId(), AirbyteProtocolVersion.getWithDefault(def.getSpec().getProtocolVersion())));
    } else {
      stream = definitionsProvider.getDestinationDefinitions()
          .stream()
          .map(def -> Map.entry(def.getDestinationDefinitionId(), AirbyteProtocolVersion.getWithDefault(def.getSpec().getProtocolVersion())));
    }
    return stream;
  }

  private Stream<String> formatActorDefinitionForLogging(final Set<UUID> remainingDestConflicts, final Set<UUID> remainingSourceConflicts) {
    return Stream.concat(
        remainingSourceConflicts.stream().map(defId -> {
          final StandardSourceDefinition sourceDef;
          try {
            sourceDef = configRepository.getStandardSourceDefinition(defId);
            return String.format("Source: %s: %s: protocol version: %s",
                sourceDef.getSourceDefinitionId(), sourceDef.getName(), sourceDef.getProtocolVersion());
          } catch (Exception e) {
            log.info("Failed to getStandardSourceDefinition for " + defId, e);
            return String.format("Source: %s: Failed to fetch details...", defId);
          }
        }),
        remainingDestConflicts.stream().map(defId -> {
          try {
            final StandardDestinationDefinition destDef = configRepository.getStandardDestinationDefinition(defId);
            return String.format("Destination: %s: %s: protocol version: %s",
                destDef.getDestinationDefinitionId(), destDef.getName(), destDef.getProtocolVersion());
          } catch (Exception e) {
            log.info("Failed to getStandardDestinationDefinition for " + defId, e);
            return String.format("Source: %s: Failed to fetch details...", defId);
          }
        }));
  }

}
