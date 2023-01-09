/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.handlers;

import io.airbyte.api.model.generated.WebBackendCheckUpdatesRead;
import io.airbyte.config.StandardDestinationDefinition;
import io.airbyte.config.StandardSourceDefinition;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.server.services.AirbyteGithubStore;
import java.io.IOException;
import java.util.List;
import java.util.Map;
import java.util.Map.Entry;
import java.util.UUID;
import java.util.stream.Collectors;
import lombok.AllArgsConstructor;
import lombok.extern.slf4j.Slf4j;

@AllArgsConstructor
@Slf4j
public class WebBackendCheckUpdatesHandler {

  private static final int NO_CHANGES_FOUND = 0;

  final ConfigRepository configRepository;
  final AirbyteGithubStore githubStore;

  public WebBackendCheckUpdatesRead checkUpdates() {

    final int destinationDiffCount = getDestinationDiffCount();
    final int sourceDiffCount = getSourceDiffCount();

    return new WebBackendCheckUpdatesRead()
        .destinationDefinitions(destinationDiffCount)
        .sourceDefinitions(sourceDiffCount);
  }

  private int getDestinationDiffCount() {
    final List<Entry<UUID, String>> currentActorDefToDockerImageTag;
    final Map<UUID, String> newActorDefToDockerImageTag;

    try {
      currentActorDefToDockerImageTag = configRepository.listStandardDestinationDefinitions(false)
          .stream()
          .map(def -> Map.entry(def.getDestinationDefinitionId(), def.getDockerImageTag()))
          .toList();
    } catch (final IOException e) {
      log.error("Failed to get current list of standard destination definitions", e);
      return NO_CHANGES_FOUND;
    }

    try {
      newActorDefToDockerImageTag = githubStore.getLatestDestinations()
          .stream()
          .collect(Collectors.toMap(StandardDestinationDefinition::getDestinationDefinitionId, StandardDestinationDefinition::getDockerImageTag));
    } catch (final InterruptedException e) {
      log.error("Failed to get latest list of standard destination definitions", e);
      return NO_CHANGES_FOUND;
    }

    return getDiffCount(currentActorDefToDockerImageTag, newActorDefToDockerImageTag);
  }

  private int getSourceDiffCount() {
    final List<Entry<UUID, String>> currentActorDefToDockerImageTag;
    final Map<UUID, String> newActorDefToDockerImageTag;

    try {
      currentActorDefToDockerImageTag = configRepository.listStandardSourceDefinitions(false)
          .stream()
          .map(def -> Map.entry(def.getSourceDefinitionId(), def.getDockerImageTag()))
          .toList();
    } catch (final IOException e) {
      log.error("Failed to get current list of standard source definitions", e);
      return NO_CHANGES_FOUND;
    }

    try {
      newActorDefToDockerImageTag = githubStore.getLatestSources()
          .stream()
          .collect(Collectors.toMap(StandardSourceDefinition::getSourceDefinitionId, StandardSourceDefinition::getDockerImageTag));
    } catch (final InterruptedException e) {
      log.error("Failed to get latest list of standard source definitions", e);
      return NO_CHANGES_FOUND;
    }

    return getDiffCount(currentActorDefToDockerImageTag, newActorDefToDockerImageTag);
  }

  private int getDiffCount(final List<Entry<UUID, String>> initialSet, final Map<UUID, String> newSet) {
    int diffCount = 0;
    for (final Entry<UUID, String> kvp : initialSet) {
      final String newDockerImageTag = newSet.get(kvp.getKey());
      if (newDockerImageTag != null && !kvp.getValue().equals(newDockerImageTag)) {
        ++diffCount;
      }
    }
    return diffCount;
  }

}
