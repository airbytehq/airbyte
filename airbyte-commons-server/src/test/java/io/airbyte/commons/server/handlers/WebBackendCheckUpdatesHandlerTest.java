/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.server.handlers;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

import io.airbyte.api.model.generated.WebBackendCheckUpdatesRead;
import io.airbyte.commons.server.services.AirbyteGithubStore;
import io.airbyte.config.StandardDestinationDefinition;
import io.airbyte.config.StandardSourceDefinition;
import io.airbyte.config.persistence.ConfigRepository;
import java.io.IOException;
import java.util.List;
import java.util.Map;
import java.util.Map.Entry;
import java.util.UUID;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class WebBackendCheckUpdatesHandlerTest {

  ConfigRepository configRepository;
  AirbyteGithubStore githubStore;
  WebBackendCheckUpdatesHandler webBackendCheckUpdatesHandler;

  final static boolean INCLUDE_TOMBSTONE = false;

  @BeforeEach
  void beforeEach() {
    configRepository = mock(ConfigRepository.class);
    githubStore = mock(AirbyteGithubStore.class);
    webBackendCheckUpdatesHandler = new WebBackendCheckUpdatesHandler(configRepository, githubStore);
  }

  @Test
  void testCheckWithoutUpdate() throws IOException, InterruptedException {
    final UUID source1 = UUID.randomUUID();
    final UUID source2 = UUID.randomUUID();
    final String sourceTag1 = "1.0.0";
    final String sourceTag2 = "2.0.0";

    final UUID dest1 = UUID.randomUUID();
    final UUID dest2 = UUID.randomUUID();
    final String destTag1 = "0.1.0";
    final String destTag2 = "0.2.0";

    setMocks(
        List.of(Map.entry(source1, sourceTag1), Map.entry(source2, sourceTag2), Map.entry(source2, sourceTag2)),
        List.of(Map.entry(source1, sourceTag1), Map.entry(source2, sourceTag2)),
        List.of(Map.entry(dest1, destTag1), Map.entry(dest2, destTag2)),
        List.of(Map.entry(dest1, destTag1), Map.entry(dest2, destTag2)));

    final WebBackendCheckUpdatesRead actual = webBackendCheckUpdatesHandler.checkUpdates();

    assertEquals(new WebBackendCheckUpdatesRead().destinationDefinitions(0).sourceDefinitions(0), actual);
  }

  @Test
  void testCheckWithUpdate() throws IOException, InterruptedException {
    final UUID source1 = UUID.randomUUID();
    final UUID source2 = UUID.randomUUID();
    final String sourceTag1 = "1.1.0";
    final String sourceTag2 = "2.1.0";

    final UUID dest1 = UUID.randomUUID();
    final UUID dest2 = UUID.randomUUID();
    final String destTag1 = "0.1.0";
    final String destTag2 = "0.2.0";

    setMocks(
        List.of(Map.entry(source1, sourceTag1), Map.entry(source2, sourceTag2), Map.entry(source2, sourceTag2)),
        List.of(Map.entry(source1, "1.1.1"), Map.entry(source2, sourceTag2)),
        List.of(Map.entry(dest1, destTag1), Map.entry(dest2, destTag2), Map.entry(dest2, destTag2)),
        List.of(Map.entry(dest1, destTag1), Map.entry(dest2, "0.3.0")));

    final WebBackendCheckUpdatesRead actual = webBackendCheckUpdatesHandler.checkUpdates();

    assertEquals(new WebBackendCheckUpdatesRead().destinationDefinitions(2).sourceDefinitions(1), actual);
  }

  @Test
  void testCheckWithMissingActorDefFromLatest() throws IOException, InterruptedException {
    final UUID source1 = UUID.randomUUID();
    final UUID source2 = UUID.randomUUID();
    final String sourceTag1 = "1.0.0";
    final String sourceTag2 = "2.0.0";

    final UUID dest1 = UUID.randomUUID();
    final UUID dest2 = UUID.randomUUID();
    final String destTag1 = "0.1.0";
    final String destTag2 = "0.2.0";

    setMocks(
        List.of(Map.entry(source1, sourceTag1), Map.entry(source2, sourceTag2), Map.entry(source2, sourceTag2)),
        List.of(Map.entry(source2, sourceTag2)),
        List.of(Map.entry(dest1, destTag1), Map.entry(dest2, destTag2)),
        List.of(Map.entry(dest1, destTag1)));

    final WebBackendCheckUpdatesRead actual = webBackendCheckUpdatesHandler.checkUpdates();

    assertEquals(new WebBackendCheckUpdatesRead().destinationDefinitions(0).sourceDefinitions(0), actual);
  }

  @Test
  void testCheckErrorNoCurrentDestinations() throws IOException, InterruptedException {
    setMocksForExceptionCases();
    when(configRepository.listStandardDestinationDefinitions(INCLUDE_TOMBSTONE)).thenThrow(new IOException("unable to read current destinations"));

    final WebBackendCheckUpdatesRead actual = webBackendCheckUpdatesHandler.checkUpdates();

    assertEquals(new WebBackendCheckUpdatesRead().destinationDefinitions(0).sourceDefinitions(1), actual);
  }

  @Test
  void testCheckErrorNoCurrentSources() throws IOException, InterruptedException {
    setMocksForExceptionCases();
    when(configRepository.listStandardSourceDefinitions(INCLUDE_TOMBSTONE)).thenThrow(new IOException("unable to read current sources"));

    final WebBackendCheckUpdatesRead actual = webBackendCheckUpdatesHandler.checkUpdates();

    assertEquals(new WebBackendCheckUpdatesRead().destinationDefinitions(1).sourceDefinitions(0), actual);
  }

  @Test
  void testCheckErrorNoLatestDestinations() throws IOException, InterruptedException {
    setMocksForExceptionCases();
    when(githubStore.getLatestDestinations()).thenThrow(new InterruptedException("unable to read latest destinations"));

    final WebBackendCheckUpdatesRead actual = webBackendCheckUpdatesHandler.checkUpdates();

    assertEquals(new WebBackendCheckUpdatesRead().destinationDefinitions(0).sourceDefinitions(1), actual);
  }

  @Test
  void testCheckErrorNoLatestSources() throws IOException, InterruptedException {
    setMocksForExceptionCases();
    when(githubStore.getLatestSources()).thenThrow(new InterruptedException("unable to read latest sources"));

    final WebBackendCheckUpdatesRead actual = webBackendCheckUpdatesHandler.checkUpdates();

    assertEquals(new WebBackendCheckUpdatesRead().destinationDefinitions(1).sourceDefinitions(0), actual);
  }

  private void setMocksForExceptionCases() throws IOException, InterruptedException {
    final UUID source1 = UUID.randomUUID();
    final String sourceTag1 = source1.toString();

    final UUID dest1 = UUID.randomUUID();
    final String destTag1 = dest1.toString();

    setMocks(
        List.of(Map.entry(source1, sourceTag1)),
        List.of(Map.entry(source1, UUID.randomUUID().toString())),
        List.of(Map.entry(dest1, destTag1)),
        List.of(Map.entry(dest1, UUID.randomUUID().toString())));
  }

  private void setMocks(final List<Entry<UUID, String>> currentSources,
                        final List<Entry<UUID, String>> latestSources,
                        final List<Entry<UUID, String>> currentDestinations,
                        final List<Entry<UUID, String>> latestDestinations)
      throws IOException, InterruptedException {
    when(configRepository.listStandardSourceDefinitions(INCLUDE_TOMBSTONE))
        .thenReturn(currentSources.stream().map(this::createSourceDef).toList());
    when(githubStore.getLatestSources())
        .thenReturn(latestSources.stream().map(this::createSourceDef).toList());

    when(configRepository.listStandardDestinationDefinitions(INCLUDE_TOMBSTONE))
        .thenReturn(currentDestinations.stream().map(this::createDestinationDef).toList());
    when(githubStore.getLatestDestinations())
        .thenReturn(latestDestinations.stream().map(this::createDestinationDef).toList());
  }

  private StandardDestinationDefinition createDestinationDef(final Entry<UUID, String> idImageTagEntry) {
    return new StandardDestinationDefinition()
        .withDestinationDefinitionId(idImageTagEntry.getKey())
        .withDockerImageTag(idImageTagEntry.getValue());
  }

  private StandardSourceDefinition createSourceDef(final Entry<UUID, String> idImageTagEntry) {
    return new StandardSourceDefinition()
        .withSourceDefinitionId(idImageTagEntry.getKey())
        .withDockerImageTag(idImageTagEntry.getValue());
  }

}
