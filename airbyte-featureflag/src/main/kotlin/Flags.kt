/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.featureflag

/**
 * If enabled, all messages from the source to the destination will be logged in 1 second intervals.
 */
object LogConnectorMessages : Flag(team = Team.PLATFORM_WORKFLOW, key = "log_connector_messages")

object StreamCapableState : EnvVar(envVar = "USE_STREAM_CAPABLE_STATE")
object AutoDetectSchema : EnvVar(team = Team.PLATFORM_WORKFLOW, envVar = "AUTO_DETECT_SCHEMA")
object NeedStateValidation : EnvVar(envVar = "NEED_STATE_VALIDATION")
object ApplyFieldSelection : EnvVar(envVar = "APPLY_FIELD_SELECTION")

/**
 * The team that created and is responsible for individual feature-flags.
 * TODO: finalize the options here!
 */
enum class Team {
    UNKNOWN,
    DESTINATIONS,
    PLATFORM_WORKFLOW,
    CLOUD,
    FRONTEND,
}

/**
 * Flag is a sealed class that all feature-flags must inherit from.
 *
 * There are two types of feature-flags; permanent and temporary. Permanent flags should inherit from the Flag class directly
 * while temporary flags should inherit from the Temporary class (which it itself inherits from the Flag class).
 *
 * @param [team] is the team that is responsible for the feature-flag, defaults to Unknown.
 * @param [key] is the globally unique identifier for identifying this specific feature-flag.
 * @param [default] is the default value of the flag.
 */
sealed class Flag(
    internal val team: Team = Team.UNKNOWN,
    internal val key: String,
    internal val default: Boolean = false,
)

/**
 * Temporary is an open class (non-final) that all temporary feature-flags should inherit from.
 *
 * A Temporary feature-flag is any feature-flag that is not intended to exist forever.
 * Most feature-flags should be considered temporary.
 *
 * @param [team] is the team that is responsible for the feature-flag, defaults to Unknown.
 * @param [key] is the globally unique identifier for identifying this specific feature-flag.
 * @param [default] is the default value of the flag.
 */
open class Temporary @JvmOverloads constructor(
    team: Team = Team.UNKNOWN,
    key: String,
    default: Boolean = false,
) : Flag(team = team, key = key, default = default)

/**
 * Environment Variable based feature-flag.
 *
 * Intended only to be used in a transitory manner as the platform migrates to an official feature-flag solution.
 * Every instance of this class should be migrated over to the Temporary class.
 *
 * @param [team] the team that controls this flag
 * @param [envVar] the environment variable to check for the status of this flag
 * @param [default] the default value of this flag, if the environment variable is not defined
 * @param [fetcher] the function used to retrieve the environment-variable, overrideable for testing purposes only
 * @constructor an internal constructor for testing purposes, users must be the public constructor
 */
open class EnvVar internal constructor(
    team: Team = Team.UNKNOWN,
    envVar: String,
    default: Boolean = false,
    private val fetcher: (String) -> String?,
) : Flag(team = team, key = envVar, default = default) {

    /**
     * Constructs an EnvVar flag
     *
     * @param [team] the team that controls this flag
     * @param [envVar] the environment variable to check for the status of this flag
     * @param [default] the default value of this flag, if the environment variable is not defined
     */
    @JvmOverloads
    constructor(
        team: Team = Team.UNKNOWN,
        envVar: String,
        default: Boolean = false,
    ) : this(team, envVar, default, { s -> System.getenv(s) })

    /**
     * Returns true if, and only if, the environment-variable is defined and evaluates to "true".  Otherwise, returns false.
     */
    internal fun enabled(): Boolean {
        return fetcher(key)
            ?.takeIf { it.isNotEmpty() }
            ?.let { it.toBoolean() }
            ?: default
    }
}