/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.bootloader;

import io.airbyte.commons.version.AirbyteProtocolVersion;
import io.airbyte.commons.version.AirbyteProtocolVersionRange;
import io.airbyte.commons.version.AirbyteVersion;
import io.airbyte.commons.version.Version;
import io.airbyte.config.ActorType;
import io.airbyte.config.StandardDestinationDefinition;
import io.airbyte.config.StandardSourceDefinition;
import io.airbyte.config.init.DefinitionsProvider;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.persistence.job.JobPersistence;
import jakarta.inject.Singleton;
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

/**
 * Validates that all connectors support the desired target Airbyte protocol version.
 */
@Singleton
@Slf4j
public class ProtocolVersionChecker {

  private final JobPersistence jobPersistence;
  private final AirbyteProtocolVersionRange airbyteProtocolTargetVersionRange;
  private final ConfigRepository configRepository;
  private final Optional<DefinitionsProvider> definitionsProvider;

  /**
   * Constructs a new protocol version checker that verifies all connectors are within the provided
   * target protocol version range.
   *
   * @param jobPersistence A {@link JobPersistence} instance.
   * @param airbyteProtocolTargetVersionRange The target Airbyte protocol version range.
   * @param configRepository A {@link ConfigRepository} instance
   * @param definitionsProvider An {@link Optional} that may contain a {@link DefinitionsProvider}
   *        instance.
   */
  public ProtocolVersionChecker(final JobPersistence jobPersistence,
                                final AirbyteProtocolVersionRange airbyteProtocolTargetVersionRange,
                                final ConfigRepository configRepository,
                                final Optional<DefinitionsProvider> definitionsProvider) {
    this.jobPersistence = jobPersistence;
    this.airbyteProtocolTargetVersionRange = airbyteProtocolTargetVersionRange;
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
    final Optional<AirbyteVersion> currentAirbyteVersion = getCurrentAirbyteVersion();
    final Optional<AirbyteProtocolVersionRange> currentRange = jobPersistence.getCurrentProtocolVersionRange();
    final AirbyteProtocolVersionRange targetRange = getTargetProtocolVersionRange();

    // Checking if there is a pre-existing version of airbyte.
    // Without this check, the first run of the validation would fail because we do not have the tables
    // set yet
    // which means that the actor definitions lookup will throw SQLExceptions.
    if (currentAirbyteVersion.isEmpty()) {
      log.info("No previous version of Airbyte detected, assuming this is a fresh deploy.");
      return Optional.of(targetRange);
    }

    if (currentRange.isEmpty() || currentRange.get().equals(targetRange)) {
      log.info("Using AirbyteProtocolVersion range [{}:{}]", targetRange.min().serialize(), targetRange.max().serialize());
      return Optional.of(targetRange);
    }

    log.info("Detected an AirbyteProtocolVersion range change from [{}:{}] to [{}:{}]",
        currentRange.get().min().serialize(), currentRange.get().max().serialize(),
        targetRange.min().serialize(), targetRange.max().serialize());

    final Map<ActorType, Set<UUID>> conflicts = getConflictingActorDefinitions(targetRange);

    if (conflicts.isEmpty()) {
      log.info("No protocol version conflict detected.");
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

  protected Optional<AirbyteVersion> getCurrentAirbyteVersion() throws IOException {
    return jobPersistence.getVersion().map(AirbyteVersion::new);
  }

  protected AirbyteProtocolVersionRange getTargetProtocolVersionRange() {
    return airbyteProtocolTargetVersionRange;
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
    if (definitionsProvider.isEmpty()) {
      return Stream.empty();
    }

    return getActorVersions(actorType);
  }

  private Stream<Entry<UUID, Version>> getActorVersions(final ActorType actorType) {
    switch (actorType) {
      case SOURCE:
        return definitionsProvider.get().getSourceDefinitions()
            .stream()
            .map(def -> Map.entry(def.getSourceDefinitionId(), AirbyteProtocolVersion.getWithDefault(def.getSpec().getProtocolVersion())));
      case DESTINATION:
      default:
        return definitionsProvider.get().getDestinationDefinitions()
            .stream()
            .map(def -> Map.entry(def.getDestinationDefinitionId(), AirbyteProtocolVersion.getWithDefault(def.getSpec().getProtocolVersion())));
    }
  }

  private Stream<String> formatActorDefinitionForLogging(final Set<UUID> remainingDestConflicts, final Set<UUID> remainingSourceConflicts) {
    return Stream.concat(
        remainingSourceConflicts.stream().map(defId -> {
          final StandardSourceDefinition sourceDef;
          try {
            sourceDef = configRepository.getStandardSourceDefinition(defId);
            return String.format("Source: %s: %s: protocol version: %s",
                sourceDef.getSourceDefinitionId(), sourceDef.getName(), sourceDef.getProtocolVersion());
          } catch (final Exception e) {
            log.info("Failed to getStandardSourceDefinition for {}", defId, e);
            return String.format("Source: %s: Failed to fetch details...", defId);
          }
        }),
        remainingDestConflicts.stream().map(defId -> {
          try {
            final StandardDestinationDefinition destDef = configRepository.getStandardDestinationDefinition(defId);
            return String.format("Destination: %s: %s: protocol version: %s",
                destDef.getDestinationDefinitionId(), destDef.getName(), destDef.getProtocolVersion());
          } catch (final Exception e) {
            log.info("Failed to getStandardDestinationDefinition for {}", defId, e);
            return String.format("Source: %s: Failed to fetch details...", defId);
          }
        }));
  }

}
