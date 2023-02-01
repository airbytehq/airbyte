/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.bootloader;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

import io.airbyte.commons.version.AirbyteProtocolVersionRange;
import io.airbyte.commons.version.Version;
import io.airbyte.config.ActorType;
import io.airbyte.config.StandardDestinationDefinition;
import io.airbyte.config.StandardSourceDefinition;
import io.airbyte.config.init.DefinitionsProvider;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.persistence.job.JobPersistence;
import io.airbyte.protocol.models.ConnectorSpecification;
import java.io.IOException;
import java.util.List;
import java.util.Map;
import java.util.Map.Entry;
import java.util.Optional;
import java.util.Set;
import java.util.UUID;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.ValueSource;

class ProtocolVersionCheckerTest {

  ConfigRepository configRepository;
  DefinitionsProvider definitionsProvider;
  JobPersistence jobPersistence;

  final Version V0_0_0 = new Version("0.0.0");
  final Version V1_0_0 = new Version("1.0.0");
  final Version V2_0_0 = new Version("2.0.0");

  @BeforeEach
  void beforeEach() throws IOException {
    configRepository = mock(ConfigRepository.class);
    definitionsProvider = mock(DefinitionsProvider.class);
    jobPersistence = mock(JobPersistence.class);

    when(jobPersistence.getVersion()).thenReturn(Optional.of("1.2.3"));
  }

  @ParameterizedTest
  @ValueSource(booleans = {true, false})
  void testFirstInstallCheck(final boolean supportAutoUpgrade) throws IOException {
    final AirbyteProtocolVersionRange expectedRange = new AirbyteProtocolVersionRange(V0_0_0, V1_0_0);
    when(jobPersistence.getVersion()).thenReturn(Optional.empty());
    final ProtocolVersionChecker protocolVersionChecker =
        new ProtocolVersionChecker(jobPersistence, expectedRange, configRepository, Optional.of(definitionsProvider));
    final Optional<AirbyteProtocolVersionRange> supportedRange = protocolVersionChecker.validate(supportAutoUpgrade);
    assertTrue(supportedRange.isPresent());
    assertEquals(expectedRange.max(), supportedRange.get().max());
    assertEquals(expectedRange.min(), supportedRange.get().min());
  }

  @Test
  void testGetTargetRange() throws IOException {
    final AirbyteProtocolVersionRange expectedRange = new AirbyteProtocolVersionRange(V1_0_0, V2_0_0);
    final ProtocolVersionChecker protocolVersionChecker =
        new ProtocolVersionChecker(jobPersistence, expectedRange, configRepository, Optional.of(definitionsProvider));
    assertEquals(expectedRange.max(), protocolVersionChecker.getTargetProtocolVersionRange().max());
    assertEquals(expectedRange.min(), protocolVersionChecker.getTargetProtocolVersionRange().min());
  }

  @Test
  void testRetrievingCurrentConflicts() throws IOException {
    final AirbyteProtocolVersionRange targetRange = new AirbyteProtocolVersionRange(V1_0_0, V2_0_0);

    final UUID source1 = UUID.randomUUID();
    final UUID source2 = UUID.randomUUID();
    final UUID source3 = UUID.randomUUID();
    final UUID dest1 = UUID.randomUUID();
    final UUID dest2 = UUID.randomUUID();

    final Map<UUID, Entry<ActorType, Version>> initialActorDefinitions = Map.of(
        source1, Map.entry(ActorType.SOURCE, V0_0_0),
        source2, Map.entry(ActorType.SOURCE, V1_0_0),
        source3, Map.entry(ActorType.SOURCE, V2_0_0),
        dest1, Map.entry(ActorType.DESTINATION, V0_0_0),
        dest2, Map.entry(ActorType.DESTINATION, V0_0_0));
    when(configRepository.getActorDefinitionToProtocolVersionMap()).thenReturn(initialActorDefinitions);

    final ProtocolVersionChecker protocolVersionChecker =
        new ProtocolVersionChecker(jobPersistence, targetRange, configRepository, Optional.of(definitionsProvider));
    final Map<ActorType, Set<UUID>> conflicts = protocolVersionChecker.getConflictingActorDefinitions(targetRange);

    final Map<ActorType, Set<UUID>> expectedConflicts = Map.of(
        ActorType.DESTINATION, Set.of(dest1, dest2),
        ActorType.SOURCE, Set.of(source1));
    assertEquals(expectedConflicts, conflicts);
  }

  @Test
  void testRetrievingCurrentConflictsWhenNoConflicts() throws IOException {
    final AirbyteProtocolVersionRange targetRange = new AirbyteProtocolVersionRange(V1_0_0, V2_0_0);

    final UUID source1 = UUID.randomUUID();
    final UUID dest1 = UUID.randomUUID();

    final Map<UUID, Entry<ActorType, Version>> initialActorDefinitions = Map.of(
        source1, Map.entry(ActorType.SOURCE, V2_0_0),
        dest1, Map.entry(ActorType.DESTINATION, V1_0_0));
    when(configRepository.getActorDefinitionToProtocolVersionMap()).thenReturn(initialActorDefinitions);

    final ProtocolVersionChecker protocolVersionChecker =
        new ProtocolVersionChecker(jobPersistence, targetRange, configRepository, Optional.of(definitionsProvider));
    final Map<ActorType, Set<UUID>> conflicts = protocolVersionChecker.getConflictingActorDefinitions(targetRange);

    assertEquals(Map.of(), conflicts);
  }

  @Test
  void testProjectRemainingSourceConflicts() {
    final AirbyteProtocolVersionRange targetRange = new AirbyteProtocolVersionRange(V1_0_0, V2_0_0);

    final UUID unrelatedSource = UUID.randomUUID();
    final UUID upgradedSource = UUID.randomUUID();
    final UUID notChangedSource = UUID.randomUUID();
    final UUID missingSource = UUID.randomUUID();
    final Set<UUID> initialConflicts = Set.of(upgradedSource, notChangedSource, missingSource);

    setNewSourceDefinitions(List.of(
        Map.entry(unrelatedSource, V2_0_0),
        Map.entry(upgradedSource, V1_0_0),
        Map.entry(notChangedSource, V0_0_0)));

    final ProtocolVersionChecker protocolVersionChecker =
        new ProtocolVersionChecker(jobPersistence, targetRange, configRepository, Optional.of(definitionsProvider));
    final Set<UUID> actualConflicts =
        protocolVersionChecker.projectRemainingConflictsAfterConnectorUpgrades(targetRange, initialConflicts, ActorType.SOURCE);

    final Set<UUID> expectedConflicts = Set.of(notChangedSource, missingSource);
    assertEquals(expectedConflicts, actualConflicts);
  }

  @Test
  void testProjectRemainingDestinationConflicts() {
    final AirbyteProtocolVersionRange targetRange = new AirbyteProtocolVersionRange(V1_0_0, V2_0_0);

    final UUID dest1 = UUID.randomUUID();
    final UUID dest2 = UUID.randomUUID();
    final UUID dest3 = UUID.randomUUID();
    final Set<UUID> initialConflicts = Set.of(dest1, dest2, dest3);

    setNewDestinationDefinitions(List.of(
        Map.entry(dest1, V2_0_0),
        Map.entry(dest2, V1_0_0),
        Map.entry(dest3, V2_0_0)));

    final ProtocolVersionChecker protocolVersionChecker =
        new ProtocolVersionChecker(jobPersistence, targetRange, configRepository, Optional.of(definitionsProvider));
    final Set<UUID> actualConflicts =
        protocolVersionChecker.projectRemainingConflictsAfterConnectorUpgrades(targetRange, initialConflicts, ActorType.DESTINATION);

    final Set<UUID> expectedConflicts = Set.of();
    assertEquals(expectedConflicts, actualConflicts);
  }

  @ParameterizedTest
  @ValueSource(booleans = {true, false})
  void testValidateSameRange(final boolean supportAutoUpgrade) throws Exception {
    final AirbyteProtocolVersionRange expectedRange = new AirbyteProtocolVersionRange(V0_0_0, V2_0_0);
    setCurrentProtocolRangeRange(expectedRange.min(), expectedRange.max());
    final ProtocolVersionChecker protocolVersionChecker =
        new ProtocolVersionChecker(jobPersistence, expectedRange, configRepository, Optional.of(definitionsProvider));

    final Optional<AirbyteProtocolVersionRange> supportedRange = protocolVersionChecker.validate(supportAutoUpgrade);
    assertTrue(supportedRange.isPresent());
    assertEquals(expectedRange.max(), supportedRange.get().max());
    assertEquals(expectedRange.min(), supportedRange.get().min());
  }

  @ParameterizedTest
  @ValueSource(booleans = {true, false})
  void testValidateAllConnectorsAreUpgraded(final boolean supportAutoUpgrade) throws Exception {
    setCurrentProtocolRangeRange(V0_0_0, V1_0_0);

    final UUID source1 = UUID.randomUUID();
    final UUID source2 = UUID.randomUUID();
    final UUID source3 = UUID.randomUUID();
    final UUID source4 = UUID.randomUUID();
    final UUID dest1 = UUID.randomUUID();
    final UUID dest2 = UUID.randomUUID();
    final UUID dest3 = UUID.randomUUID();
    final AirbyteProtocolVersionRange expectedTargetVersionRange = new AirbyteProtocolVersionRange(V1_0_0, V2_0_0);

    final Map<UUID, Entry<ActorType, Version>> initialActorDefinitions = Map.of(
        source1, Map.entry(ActorType.SOURCE, V0_0_0),
        source2, Map.entry(ActorType.SOURCE, V1_0_0),
        source3, Map.entry(ActorType.SOURCE, V0_0_0),
        source4, Map.entry(ActorType.SOURCE, V0_0_0),
        dest1, Map.entry(ActorType.DESTINATION, V0_0_0),
        dest2, Map.entry(ActorType.DESTINATION, V1_0_0),
        dest3, Map.entry(ActorType.DESTINATION, V2_0_0));
    when(configRepository.getActorDefinitionToProtocolVersionMap()).thenReturn(initialActorDefinitions);

    setNewSourceDefinitions(List.of(
        Map.entry(source1, V1_0_0),
        Map.entry(source2, V1_0_0),
        Map.entry(source3, V2_0_0),
        Map.entry(source4, V1_0_0)));
    setNewDestinationDefinitions(List.of(
        Map.entry(dest1, V1_0_0),
        Map.entry(dest2, V1_0_0),
        Map.entry(dest3, V2_0_0)));

    final ProtocolVersionChecker protocolVersionChecker =
        new ProtocolVersionChecker(jobPersistence, expectedTargetVersionRange, configRepository, Optional.of(definitionsProvider));
    final Optional<AirbyteProtocolVersionRange> actualRange = protocolVersionChecker.validate(supportAutoUpgrade);

    // Without auto upgrade, we will fail the validation because it would require connector automatic
    // actor definition
    // upgrade for used sources/destinations.
    if (supportAutoUpgrade) {
      assertTrue(actualRange.isPresent());
      assertEquals(expectedTargetVersionRange.max(), actualRange.get().max());
      assertEquals(expectedTargetVersionRange.min(), actualRange.get().min());
    } else {
      assertEquals(Optional.empty(), actualRange);
    }
  }

  @ParameterizedTest
  @ValueSource(booleans = {true, false})
  void testValidateBadUpgradeMissingSource(final boolean supportAutoUpgrade) throws Exception {
    final AirbyteProtocolVersionRange expectedTargetVersionRange = new AirbyteProtocolVersionRange(V1_0_0, V2_0_0);
    setCurrentProtocolRangeRange(V0_0_0, V1_0_0);

    final UUID source1 = UUID.randomUUID();
    final UUID source2 = UUID.randomUUID();
    final UUID dest1 = UUID.randomUUID();
    final UUID dest2 = UUID.randomUUID();

    final Map<UUID, Entry<ActorType, Version>> initialActorDefinitions = Map.of(
        source1, Map.entry(ActorType.SOURCE, V0_0_0),
        source2, Map.entry(ActorType.SOURCE, V0_0_0),
        dest1, Map.entry(ActorType.DESTINATION, V0_0_0),
        dest2, Map.entry(ActorType.DESTINATION, V0_0_0));
    when(configRepository.getActorDefinitionToProtocolVersionMap()).thenReturn(initialActorDefinitions);

    setNewSourceDefinitions(List.of(
        Map.entry(source1, V0_0_0),
        Map.entry(source2, V1_0_0)));
    setNewDestinationDefinitions(List.of(
        Map.entry(dest1, V1_0_0),
        Map.entry(dest2, V1_0_0)));

    final ProtocolVersionChecker protocolVersionChecker =
        new ProtocolVersionChecker(jobPersistence, expectedTargetVersionRange, configRepository, Optional.of(definitionsProvider));
    final Optional<AirbyteProtocolVersionRange> actualRange = protocolVersionChecker.validate(supportAutoUpgrade);
    assertEquals(Optional.empty(), actualRange);
  }

  @ParameterizedTest
  @ValueSource(booleans = {true, false})
  void testValidateBadUpgradeMissingDestination(final boolean supportAutoUpgrade) throws Exception {
    final AirbyteProtocolVersionRange expectedTargetVersionRange = new AirbyteProtocolVersionRange(V1_0_0, V2_0_0);
    setCurrentProtocolRangeRange(V0_0_0, V1_0_0);

    final UUID source1 = UUID.randomUUID();
    final UUID source2 = UUID.randomUUID();
    final UUID dest1 = UUID.randomUUID();
    final UUID dest2 = UUID.randomUUID();

    final Map<UUID, Entry<ActorType, Version>> initialActorDefinitions = Map.of(
        source1, Map.entry(ActorType.SOURCE, V0_0_0),
        source2, Map.entry(ActorType.SOURCE, V0_0_0),
        dest1, Map.entry(ActorType.DESTINATION, V0_0_0),
        dest2, Map.entry(ActorType.DESTINATION, V0_0_0));
    when(configRepository.getActorDefinitionToProtocolVersionMap()).thenReturn(initialActorDefinitions);

    setNewSourceDefinitions(List.of(
        Map.entry(source1, V1_0_0),
        Map.entry(source2, V1_0_0)));
    setNewDestinationDefinitions(List.of(
        Map.entry(dest1, V1_0_0),
        Map.entry(dest2, V0_0_0)));

    final ProtocolVersionChecker protocolVersionChecker =
        new ProtocolVersionChecker(jobPersistence, expectedTargetVersionRange, configRepository, Optional.of(definitionsProvider));
    final Optional<AirbyteProtocolVersionRange> actualRange = protocolVersionChecker.validate(supportAutoUpgrade);
    assertEquals(Optional.empty(), actualRange);
  }

  @ParameterizedTest
  @ValueSource(booleans = {true, false})
  void testValidateFailsOnProtocolRangeChangeWithoutDefinitionsProvider(final boolean supportAutoUpgrade) throws Exception {
    final AirbyteProtocolVersionRange expectedTargetVersionRange = new AirbyteProtocolVersionRange(V1_0_0, V2_0_0);
    setCurrentProtocolRangeRange(V0_0_0, V1_0_0);
    final ProtocolVersionChecker protocolVersionChecker =
        new ProtocolVersionChecker(jobPersistence, expectedTargetVersionRange, configRepository, Optional.empty());

    final UUID source1 = UUID.randomUUID();
    final UUID dest1 = UUID.randomUUID();

    final Map<UUID, Entry<ActorType, Version>> initialActorDefinitions = Map.of(
        source1, Map.entry(ActorType.SOURCE, V0_0_0),
        dest1, Map.entry(ActorType.DESTINATION, V0_0_0));
    when(configRepository.getActorDefinitionToProtocolVersionMap()).thenReturn(initialActorDefinitions);

    final Optional<AirbyteProtocolVersionRange> actualRange = protocolVersionChecker.validate(supportAutoUpgrade);
    assertEquals(Optional.empty(), actualRange);
  }

  @ParameterizedTest
  @ValueSource(booleans = {true, false})
  void testValidateSucceedsWhenNoProtocolRangeChangeWithoutDefinitionsProvider(final boolean supportAutoUpgrade) throws Exception {
    final AirbyteProtocolVersionRange expectedTargetVersionRange = new AirbyteProtocolVersionRange(V0_0_0, V2_0_0);
    setCurrentProtocolRangeRange(V0_0_0, V2_0_0);
    final ProtocolVersionChecker protocolVersionChecker =
        new ProtocolVersionChecker(jobPersistence, expectedTargetVersionRange, configRepository, Optional.empty());

    final UUID source1 = UUID.randomUUID();
    final UUID dest1 = UUID.randomUUID();

    final Map<UUID, Entry<ActorType, Version>> initialActorDefinitions = Map.of(
        source1, Map.entry(ActorType.SOURCE, V0_0_0),
        dest1, Map.entry(ActorType.DESTINATION, V0_0_0));
    when(configRepository.getActorDefinitionToProtocolVersionMap()).thenReturn(initialActorDefinitions);

    final Optional<AirbyteProtocolVersionRange> actualRange = protocolVersionChecker.validate(supportAutoUpgrade);
    assertTrue(actualRange.isPresent());
    assertEquals(expectedTargetVersionRange.max(), actualRange.get().max());
    assertEquals(expectedTargetVersionRange.min(), actualRange.get().min());
  }

  private void setCurrentProtocolRangeRange(final Version min, final Version max) throws IOException {
    when(jobPersistence.getCurrentProtocolVersionRange()).thenReturn(Optional.of(new AirbyteProtocolVersionRange(min, max)));
    when(jobPersistence.getAirbyteProtocolVersionMin()).thenReturn(Optional.of(min));
    when(jobPersistence.getAirbyteProtocolVersionMax()).thenReturn(Optional.of(max));
  }

  private void setNewDestinationDefinitions(final List<Entry<UUID, Version>> defs) {
    final List<StandardDestinationDefinition> destDefinitions = defs.stream()
        .map(e -> new StandardDestinationDefinition()
            .withDestinationDefinitionId(e.getKey())
            .withSpec(new ConnectorSpecification().withProtocolVersion(e.getValue().serialize())))
        .toList();
    when(definitionsProvider.getDestinationDefinitions()).thenReturn(destDefinitions);
  }

  private void setNewSourceDefinitions(final List<Entry<UUID, Version>> defs) {
    final List<StandardSourceDefinition> sourceDefinitions = defs.stream()
        .map(e -> new StandardSourceDefinition()
            .withSourceDefinitionId(e.getKey())
            .withSpec(new ConnectorSpecification().withProtocolVersion(e.getValue().serialize())))
        .toList();
    when(definitionsProvider.getSourceDefinitions()).thenReturn(sourceDefinitions);
  }

}
