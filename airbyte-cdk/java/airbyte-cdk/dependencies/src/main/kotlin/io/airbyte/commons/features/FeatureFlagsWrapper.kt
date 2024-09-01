/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.commons.features

open class FeatureFlagsWrapper(private val wrapped: FeatureFlags) : FeatureFlags {
    override fun autoDetectSchema(): Boolean {
        return wrapped.autoDetectSchema()
    }

    override fun logConnectorMessages(): Boolean {
        return wrapped.logConnectorMessages()
    }

    override fun concurrentSourceStreamRead(): Boolean {
        return wrapped.concurrentSourceStreamRead()
    }

    override fun applyFieldSelection(): Boolean {
        return wrapped.applyFieldSelection()
    }

    override fun fieldSelectionWorkspaces(): String {
        return wrapped.fieldSelectionWorkspaces()
    }

    override fun strictComparisonNormalizationWorkspaces(): String? {
        return wrapped.strictComparisonNormalizationWorkspaces()
    }

    override fun strictComparisonNormalizationTag(): String? {
        return wrapped.strictComparisonNormalizationTag()
    }

    override fun deploymentMode(): String? {
        return wrapped.deploymentMode()
    }

    companion object {
        /** Overrides the [FeatureFlags.deploymentMode] method in the feature flags. */
        @JvmStatic
        fun overridingDeploymentMode(wrapped: FeatureFlags, deploymentMode: String?): FeatureFlags {
            return object : FeatureFlagsWrapper(wrapped) {
                override fun deploymentMode(): String? {
                    return deploymentMode
                }
            }
        }
    }
}
