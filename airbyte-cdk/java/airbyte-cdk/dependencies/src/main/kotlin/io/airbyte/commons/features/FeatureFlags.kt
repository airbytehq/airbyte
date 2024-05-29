/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.commons.features

/**
 * Interface that describe which features are activated in airbyte. Currently, the only
 * implementation relies on env. Ideally it should be on some DB.
 */
interface FeatureFlags {
    fun autoDetectSchema(): Boolean

    fun logConnectorMessages(): Boolean

    fun concurrentSourceStreamRead(): Boolean

    /**
     * Return true if field selection should be applied. See also fieldSelectionWorkspaces.
     *
     * @return whether field selection should be applied
     */
    fun applyFieldSelection(): Boolean

    /**
     * Get the workspaces allow-listed for field selection. This should take precedence over
     * applyFieldSelection.
     *
     * @return a comma-separated list of workspace ids where field selection should be enabled.
     */
    fun fieldSelectionWorkspaces(): String

    /**
     * Get the workspaces allow-listed for strict incremental comparison in normalization. This
     * takes precedence over the normalization version in destination_definitions.yaml.
     *
     * @return a comma-separated list of workspace ids where strict incremental comparison should be
     * enabled in normalization.
     */
    fun strictComparisonNormalizationWorkspaces(): String?

    /**
     * Get the Docker image tag representing the normalization version with strict-comparison.
     *
     * @return The Docker image tag representing the normalization version with strict-comparison
     */
    fun strictComparisonNormalizationTag(): String?

    /**
     * Get the deployment mode used to deploy a connector.
     *
     * @return empty string for the default deployment mode, "CLOUD" for cloud deployment mode.
     */
    fun deploymentMode(): String?
}
