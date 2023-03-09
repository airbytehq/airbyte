/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.featureflag

/**
 * If enabled, all messages from the source to the destination will be logged in 1 second intervals.
 *
 * This is a permanent flag and would implement the [Flag] type once converted from an environment-variable.
 */
object LogConnectorMessages : EnvVar(envVar = "LOG_CONNECTOR_MESSAGES")

object StreamCapableState : EnvVar(envVar = "USE_STREAM_CAPABLE_STATE")
object AutoDetectSchema : EnvVar(envVar = "AUTO_DETECT_SCHEMA")
object NeedStateValidation : EnvVar(envVar = "NEED_STATE_VALIDATION")
object ApplyFieldSelection : EnvVar(envVar = "APPLY_FIELD_SELECTION")

object PerfBackgroundJsonValidation : Temporary(key = "performance.backgroundJsonSchemaValidation")

object FieldSelectionWorkspaces : EnvVar(envVar = "FIELD_SELECTION_WORKSPACES") {
    override fun enabled(ctx: Context): Boolean {
        val enabledWorkspaceIds: List<String> = fetcher(key)
            ?.takeIf { it.isNotEmpty() }
            ?.split(",")
            ?: listOf()

        val contextWorkspaceIds: List<String> = when (ctx) {
            is Multi -> ctx.fetchContexts<Workspace>().map { it.key }
            is Workspace -> listOf(ctx.key)
            else -> listOf()
        }

        return when (contextWorkspaceIds.any { it in enabledWorkspaceIds }) {
            true -> true
            else -> default
        }
    }
}

/**
 * Flag is a sealed class that all feature-flags must inherit from.
 *
 * There are two types of feature-flags; permanent and temporary. Permanent flags should inherit from the Flag class directly
 * while temporary flags should inherit from the Temporary class (which it itself inherits from the Flag class).
 *
 * @param [key] is the globally unique identifier for identifying this specific feature-flag.
 * @param [default] is the default value of the flag.
 * @param [attrs] optional attributes associated with this flag
 */
sealed class Flag(
    internal val key: String,
    internal val default: Boolean = false,
    internal val attrs: Map<String, String> = mapOf(),
)

/**
 * Temporary is an open class (non-final) that all temporary feature-flags should inherit from.
 *
 * A Temporary feature-flag is any feature-flag that is not intended to exist forever.
 * Most feature-flags should be considered temporary.
 *
 * @param [key] is the globally unique identifier for identifying this specific feature-flag.
 * @param [default] is the default value of the flag.
 * @param [attrs] attributes associated with this flag
 */
open class Temporary @JvmOverloads constructor(
    key: String,
    default: Boolean = false,
    attrs: Map<String, String> = mapOf(),
) : Flag(key = key, default = default, attrs = attrs)

/**
 * Environment-Variable based feature-flag.
 *
 * Intended only to be used in a transitory manner as the platform migrates to an official feature-flag solution.
 * Every instance of this class should be migrated over to the Temporary class.
 *
 * @param [envVar] the environment variable to check for the status of this flag
 * @param [default] the default value of this flag, if the environment variable is not defined
 * @param [attrs] attributes associated with this flag
 */
open class EnvVar @JvmOverloads constructor(
    envVar: String,
    default: Boolean = false,
    attrs: Map<String, String> = mapOf(),
) : Flag(key = envVar, default = default, attrs = attrs) {
    /**
     * Function used to retrieve the environment-variable, overrideable for testing purposes only.
     *
     * This is internal so that it can be modified for unit-testing purposes only!
     */
    internal var fetcher: (String) -> String? = { s -> System.getenv(s) }

    /**
     * Returns true if, and only if, the environment-variable is defined and evaluates to "true".  Otherwise, returns false.
     */
    internal open fun enabled(ctx: Context): Boolean {
        return fetcher(key)
            ?.takeIf { it.isNotEmpty() }
            ?.let { it.toBoolean() }
            ?: default
    }
}
