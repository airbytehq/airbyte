/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.commons.features

import io.github.oshai.kotlinlogging.KotlinLogging
import java.nio.file.Path
import java.util.function.Function

private val log = KotlinLogging.logger {}

class EnvVariableFeatureFlags : FeatureFlags {
    override fun autoDetectSchema(): Boolean {
        return getEnvOrDefault(AUTO_DETECT_SCHEMA, true) { s: String -> s.toBoolean() }
    }

    override fun logConnectorMessages(): Boolean {
        return getEnvOrDefault(LOG_CONNECTOR_MESSAGES, false) { s: String -> s.toBoolean() }
    }

    override fun concurrentSourceStreamRead(): Boolean {
        return getEnvOrDefault(CONCURRENT_SOURCE_STREAM_READ, false) { s: String -> s.toBoolean() }
    }

    override fun applyFieldSelection(): Boolean {
        return getEnvOrDefault(APPLY_FIELD_SELECTION, false) { s: String -> s.toBoolean() }
    }

    override fun fieldSelectionWorkspaces(): String {
        return getEnvOrDefault(FIELD_SELECTION_WORKSPACES, "") { arg: String -> arg }
    }

    override fun strictComparisonNormalizationWorkspaces(): String? {
        return getEnvOrDefault(STRICT_COMPARISON_NORMALIZATION_WORKSPACES, "") { arg: String ->
            arg
        }
    }

    override fun strictComparisonNormalizationTag(): String? {
        return getEnvOrDefault(STRICT_COMPARISON_NORMALIZATION_TAG, "strict_comparison2") {
            arg: String ->
            arg
        }
    }

    override fun deploymentMode(): String? {
        return getEnvOrDefault(DEPLOYMENT_MODE, "") { arg: String -> arg }
    }

    override fun airbyteStagingDirectory(): Path? {
        return getEnvOrDefault(AIRBYTE_STAGING_DIRECTORY_PROPERTY_NAME, null) { arg: String ->
            Path.of(arg)
        }
    }

    override fun useFileTransfer(): Boolean {
        return getEnvOrDefault(USE_FILE_TRANSFER, false) { it.toBoolean() }
    }

    // TODO: refactor in order to use the same method than the ones in EnvConfigs.java
    fun <T> getEnvOrDefault(key: String?, defaultValue: T, parser: Function<String, T>): T {
        val value = System.getenv(key)
        if (value != null && !value.isEmpty()) {
            return parser.apply(value)
        } else {
            log.debug { "Using default value for environment variable $key: '$defaultValue'" }
            return defaultValue
        }
    }

    companion object {

        const val AUTO_DETECT_SCHEMA: String = "AUTO_DETECT_SCHEMA"

        // Set this value to true to see all messages from the source to destination, set to one
        // second
        // emission
        const val LOG_CONNECTOR_MESSAGES: String = "LOG_CONNECTOR_MESSAGES"
        const val APPLY_FIELD_SELECTION: String = "APPLY_FIELD_SELECTION"
        const val FIELD_SELECTION_WORKSPACES: String = "FIELD_SELECTION_WORKSPACES"
        const val CONCURRENT_SOURCE_STREAM_READ: String = "CONCURRENT_SOURCE_STREAM_READ"
        const val STRICT_COMPARISON_NORMALIZATION_WORKSPACES: String =
            "STRICT_COMPARISON_NORMALIZATION_WORKSPACES"
        const val STRICT_COMPARISON_NORMALIZATION_TAG: String =
            "STRICT_COMPARISON_NORMALIZATION_TAG"
        const val DEPLOYMENT_MODE: String = "DEPLOYMENT_MODE"
        val DEFAULT_AIRBYTE_STAGING_DIRECTORY: Path = Path.of("/staging/files")
        const val AIRBYTE_STAGING_DIRECTORY_PROPERTY_NAME: String = "AIRBYTE_STAGING_DIRECTORY"
        const val USE_FILE_TRANSFER = "USE_FILE_TRANSFER"
    }
}
