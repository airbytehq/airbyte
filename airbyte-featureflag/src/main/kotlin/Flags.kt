/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.featureflag

/**
 * Team that may own a feature-flag declaration
 */
sealed class Team {
    object Unknown : Team()
    object Destinations : Team()
    object PlatformWorkflow : Team()
    object Cloud : Team()
    object Frontend : Team()
}

/**
 * Flag is a sealed class that all feature-flags must inherit from.
 *
 * There are two types of feature-flags; permanent and temporary. Permanent flags should inherit from the Flag class directly
 * while temporary flags shuold inherit from the Temporary class (which it itself inherits from the Flag class).
 *
 * @param team is the team that is responsible for the feature-flag, defaults to Unknown.
 * @param key is the globally unique identifier for identifying this specific feature-flag.
 * @param default is the default value of the flag.
 */
sealed class Flag(
    internal val team: Team = Team.Unknown,
    internal val key: String,
    internal val default: Boolean = false,
) {
    /**
     * If enabled, all messages from the source to the destination will be logged in 1 second intervals.
     */
    object LogConnectorMessages : Flag(team = Team.PlatformWorkflow, key = "log_connector_messages")
}

/**
 * Temporary is an open class (non-final) that all temporary feature-flags should inherit from.
 */
open class Temporary @JvmOverloads constructor(
    team: Team = Team.Unknown,
    key: String,
    default: Boolean = false,
) : Flag(team = team, key = key, default = default)

/**
 * Environment Variable based feature-flag.
 *
 * Intended only to be used in a transitory manner as the platform migrates to an official feature-flag solution.
 * Every instance of this class should be migrated over to the Temporary class.
 */
open class EnvVar @JvmOverloads constructor(
    team: Team = Team.Unknown,
    envVar: String,
    default: Boolean = false,
) : Flag(team = team, key = envVar, default = default) {
    /**
     * Returns true if, and only if, the environment-variable is defined and evaluates to "true".  Otherwise, returns false.
     */
    internal fun enabled(): Boolean {
        return System.getenv(key)
            ?.takeIf { it.isNotEmpty() }
            ?.let { it.toBoolean() }
            ?: default
    }
}

object StreamCapableState : EnvVar(envVar = "USE_STEAM_CAPABLE_STATE")
object AutoDetectSchema : EnvVar(team = Team.PlatformWorkflow, envVar = "AUTO_DETECT_SCHEMA")
object NeedStateValidation : EnvVar(envVar = "NEED_STATE_VALIDATION")
object ApplyFieldSelection : EnvVar(envVar = "APPLY_FIELD_SELECTION")

