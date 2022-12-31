/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.featureflag

import com.fasterxml.jackson.databind.ObjectMapper
import com.fasterxml.jackson.dataformat.yaml.YAMLFactory
import com.fasterxml.jackson.module.kotlin.readValue
import com.fasterxml.jackson.module.kotlin.registerKotlinModule
import com.launchdarkly.sdk.ContextKind
import com.launchdarkly.sdk.LDContext
import com.launchdarkly.sdk.LDUser
import com.launchdarkly.sdk.server.LDClient
import java.nio.file.Path
import java.util.concurrent.locks.ReentrantReadWriteLock
import kotlin.concurrent.read

///**
// * How I'm envisioning this working (currently, still very much a POC/rough):
// */
//class ExampleController(private val ffClient: Client) {
//    fun get(userId: String): String {
//        if (ffClient.enabled(Flag.FeatureOne, User(userId), false)) {
//            return "feature enabled"
//        }
//        return "feature not enabled"
//    }
//}

/**
 * Open Questions:
 * 1. Can the context and flag be combined into one class?
 *   - i.e. Does it make sense to one a feature-flag apply to two different context types?
 * 2. Should the default value be merged into the Flag type instead of specified on each check?
 *   - Or maybe still allow it to be specified, but make it an optional parameter
 */

/**
 * Flag contains all the feature-flags utilized by the code.
 */
//sealed class Flag(internal val key: String) {
//    object FeatureOne : Flag("feature-one")
//    object FeatureTwo : Flag("feature-two")
//    class Temp(key: String) : Flag(key)
//}

/**
 * Context abstraction around LaunchDarkly v6 context idea
 *
 * I'm still playing around with this.  Basically the idea is to define our own custom context types
 * (by implementing this sealed interface) to ensure that we are consistently using the same identifiers
 * throughout the code.
 */
sealed interface Context {
    val kind: String
    val key: String
}

/**
 * Workspace context example object
 *   where key is the unique identifier of the workspace and the account can be optionally passed as an attribute
 */
data class Workspace(override val key: String, val account: String? = null) : Context {
    override val kind = "workspace"
}

/**
 * User context example object where key is the unique identifier of the user.
 */
data class User(override val key: String) : Context {
    override val kind = "user"
}


/**
 * Feature Flag Client interfaced.
 */
sealed interface Client {
    /**
     * Returns true if the flag with the provided context should be enabled. Returns false otherwise.
     */
    fun enabled(key: Flag, ctx: Context): Boolean
}

/**
 * LaunchDarkly v5 version
 *
 * LaunchDarkly v6 introduces the LDContext class which replaces the LDUser class,
 * however this is only available to early-access users accounts currently.
 *
 * Once v6 is GA, this method would be removed and replaced with toLDContext.
 */
private fun Context.toLDUser(): LDUser {
    return LDUser(key)
}

/**
 * LaunchDarkly v6 version
 *
 * Replaces toLDUser once LaunchDarkly v6 is GA.
 */
private fun Context.toLDContext(): LDContext {
    val builder = LDContext.builder(ContextKind.of(kind), key)
    when (this) {
        is Workspace -> {
            account?.let { builder.set("account", it) }
        }

        is User -> Unit
    }
    return builder.build()
}

/**
 * LaunchDarkly implementation
 *   currently accepts a sdkKey, should instead have the LDClient provided
 */
class LD(private val client: LDClient) : Client {
    override fun enabled(flag: Flag, ctx: Context): Boolean {
        return when (flag) {
            is EnvVar -> flag.enabled()
            else -> client.boolVariation(flag.key, ctx.toLDUser(), flag.default)
        }
    }
}


/**
 * Data wrapper around OSS feature-flag configuration file.
 *
 * Files has the format of
 * flags:
 *  - name: feature-one
 *    enabled: true
 *  - name: feature-two
 *    enabled: false
 */
private data class OSSFlag(val name: String, val enabled: Boolean)

/** The yaml mapper is used for reading the feature-flag configuration file. */
private val yamlMapper = ObjectMapper(YAMLFactory()).registerKotlinModule()

/**
 * OSS implementation
 *   need to set up a file-watcher on the config to ensure changes are picked up without requiring a restart of the app
 */
class OSS(config: Path) : Client {
    /** flags contains a mapping of the flag-name to the flag properties */
    private var flags: Map<String, OSSFlag> = yamlMapper.readValue<List<OSSFlag>>(config.toFile()).associateBy { it.name }

    /** lock is used for ensuring access to the flags map is handled correctly when the map is being updated. */
    private val lock = ReentrantReadWriteLock()

    override fun enabled(flag: Flag, ctx: Context): Boolean {
        return when (flag) {
            is EnvVar -> flag.enabled()
            else -> lock.read { flags[flag.key]?.enabled ?: flag.default }
        }
    }
}
