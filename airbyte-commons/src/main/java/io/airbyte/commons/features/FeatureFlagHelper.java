/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.features;

import com.google.common.annotations.VisibleForTesting;
import java.util.HashSet;
import java.util.Set;
import java.util.UUID;
import java.util.function.Function;
import lombok.extern.slf4j.Slf4j;

@Slf4j
public class FeatureFlagHelper {

  public static boolean isFieldSelectionEnabledForWorkspace(final FeatureFlags featureFlags, final UUID workspaceId) {
    return isWorkspaceIncludedInFlag(featureFlags, FeatureFlags::fieldSelectionWorkspaces, workspaceId) || featureFlags.applyFieldSelection();
  }

  public static boolean isStrictComparisonNormalizationEnabledForWorkspace(final FeatureFlags featureFlags, final UUID workspaceId) {
    return isWorkspaceIncludedInFlag(featureFlags, FeatureFlags::strictComparisonNormalizationWorkspaces, workspaceId);
  }

  @VisibleForTesting
  static boolean isWorkspaceIncludedInFlag(final FeatureFlags featureFlags,
                                           final Function<FeatureFlags, String> flagRetriever,
                                           final UUID workspaceId) {
    final String workspaceIdsString = flagRetriever.apply(featureFlags);
    final Set<UUID> workspaceIds = new HashSet<>();
    if (workspaceIdsString != null && !workspaceIdsString.isEmpty()) {
      for (final String id : workspaceIdsString.split(",")) {
        try {
          workspaceIds.add(UUID.fromString(id));
        } catch (final IllegalArgumentException e) {
          log.warn("Malformed workspace id: {}", id);
        }
      }
    }
    return workspaceId != null && workspaceIds.contains(workspaceId);
  }

}
