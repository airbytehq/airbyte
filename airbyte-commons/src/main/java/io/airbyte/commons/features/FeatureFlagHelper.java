/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.features;

import java.util.HashSet;
import java.util.Set;
import java.util.UUID;
import lombok.extern.slf4j.Slf4j;

@Slf4j
public class FeatureFlagHelper {

  public static boolean isFieldSelectionEnabledForWorkspace(final FeatureFlags featureFlags, final UUID workspaceId) {
    final String workspaceIdsString = featureFlags.fieldSelectionWorkspaces();
    final Set<UUID> workspaceIds = new HashSet<>();
    if (workspaceIdsString != null && !workspaceIdsString.isEmpty()) {
      for (final String id : workspaceIdsString.split(",")) {
        try {
          workspaceIds.add(UUID.fromString(id));
        } catch (final IllegalArgumentException e) {
          log.warn("Malformed workspace id for field selection: {}", id);
        }
      }
    }
    if (workspaceId != null && workspaceIds.contains(workspaceId)) {
      return true;
    }

    return featureFlags.applyFieldSelection();
  }

}
