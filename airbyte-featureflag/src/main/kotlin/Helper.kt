package io.airbyte.featureflag

import io.airbyte.commons.features.FeatureFlags
import org.slf4j.Logger
import java.util.UUID
import java.util.HashSet

fun isFieldSelectionEnabledForWorkspace(flags: FeatureFlags, featureFlagClient: FeatureFlagClient, workspaceId: UUID?, log: Logger): Boolean {
    val workspaceIdsString: String? = flags.fieldSelectionWorkspaces()
    val workspaceIds: MutableSet<UUID> = HashSet()
    if (workspaceIdsString != null && !workspaceIdsString.isEmpty()) {
        for (id in workspaceIdsString.split(",".toRegex()).dropLastWhile { it.isEmpty() }.toTypedArray()) {
            try {
                workspaceIds.add(UUID.fromString(id))
            } catch (e: IllegalArgumentException) {
                log.warn("Malformed workspace id for field selection: {}", id)
            }
        }
    }

    // NOTE: the logic to determine whether a workspace should apply column selection is as follows:
    //  - If it's on the include-list (managed via environment variable), then YES
    //  - If it's not on the include-list and it is on the exclude-list (managed via FeatureFlagClient aka LaunchDarkly), then NO
    //  - Otherwise, apply the default (managed via environment variable)
    // In other words, the include-list takes precedence over the exclude-list!
    if (workspaceId != null && workspaceIds.contains(workspaceId)) {
        return true
    }
    val excludedFromFieldSelection = workspaceId != null && featureFlagClient.enabled(ColumnSelectionExcludeForUnexpectedFields, Workspace(workspaceId))
    if (excludedFromFieldSelection) {
        return false
    }
    return flags.applyFieldSelection()
}