/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.commons.features

import com.google.common.annotations.VisibleForTesting
import io.github.oshai.kotlinlogging.KotlinLogging
import java.util.*
import java.util.function.Function

private val log = KotlinLogging.logger {}

object FeatureFlagHelper {
    fun isFieldSelectionEnabledForWorkspace(
        featureFlags: FeatureFlags,
        workspaceId: UUID?
    ): Boolean {
        return (isWorkspaceIncludedInFlag(
            featureFlags,
            { obj: FeatureFlags -> obj.fieldSelectionWorkspaces() },
            workspaceId,
            "field selection"
        ) || featureFlags.applyFieldSelection())
    }

    @VisibleForTesting
    fun isWorkspaceIncludedInFlag(
        featureFlags: FeatureFlags,
        flagRetriever: Function<FeatureFlags, String?>,
        workspaceId: UUID?,
        context: String?
    ): Boolean {
        val workspaceIdsString = flagRetriever.apply(featureFlags)
        val workspaceIds: MutableSet<UUID> = HashSet()
        if (!workspaceIdsString.isNullOrEmpty()) {
            for (id in
                workspaceIdsString
                    .split(",".toRegex())
                    .dropLastWhile { it.isEmpty() }
                    .toTypedArray()) {
                try {
                    workspaceIds.add(UUID.fromString(id))
                } catch (e: IllegalArgumentException) {
                    log.warn { "Malformed workspace id for $context: $id" }
                }
            }
        }
        return workspaceId != null && workspaceIds.contains(workspaceId)
    }
}
