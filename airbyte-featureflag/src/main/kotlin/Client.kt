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
import java.lang.Thread.MIN_PRIORITY
import java.nio.file.Path
import java.nio.file.StandardWatchEventKinds
import java.util.concurrent.locks.ReentrantReadWriteLock
import kotlin.concurrent.read
import kotlin.concurrent.thread
import kotlin.concurrent.write
import kotlin.io.path.isRegularFile

/**
 * Open Questions:
 * 1. Can the context and flag be combined into one class?
 *   - i.e. Does it make sense to one a feature-flag apply to two different context types?
 * 2. Should the default value be merged into the Flag type instead of specified on each check?
 *   - Or maybe still allow it to be specified, but make it an optional parameter
 */

/**
 * Feature-Flag Client interface.
 */
sealed interface FeatureFlagClient {
    /**
     * Returns true if the flag with the provided context should be enabled. Returns false otherwise.
     */
    fun enabled(flag: Flag, ctx: Context): Boolean
}

/**
 * Config file based feature-flag client. Feature-flag are derived from a yaml config file.
 * Also supports flags defined via environment-variables via the [EnvVar] class.
 *
 * @param [config] the location of the yaml config file that contains the feature-flag definitions.
 * The [config] will be watched for changes and the internal representation of the [config] will be updated to match.
 */
class ConfigFileClient(config: Path) : FeatureFlagClient {
    /** [flags] holds the mappings of the flag-name to the flag properties */
    private var flags: Map<String, PlatformFlag> = readConfig(config)

    /** lock is used for ensuring access to the flags map is handled correctly when the map is being updated. */
    private val lock = ReentrantReadWriteLock()

    init {
        if (!config.isRegularFile()) {
            throw IllegalArgumentException("config must reference a file")
        }

        config.onChange {
            val tempFlags = readConfig(config)
            lock.write { flags = tempFlags }
        }
    }

    override fun enabled(flag: Flag, ctx: Context): Boolean {
        return when (flag) {
            is EnvVar -> flag.enabled()
            else -> lock.read { flags[flag.key]?.enabled ?: flag.default }
        }
    }
}

/**
 * LaunchDarkly based feature-flag client. Feature-flags are derived from an external source (the LDClient).
 * Also supports flags defined via environment-variables via the [EnvVar] class.
 *
 * @param [client] the Launch-Darkly client for interfacing with Launch-Darkly.
 */
class LaunchDarklyClient(private val client: LDClient) : FeatureFlagClient {
    override fun enabled(flag: Flag, ctx: Context): Boolean {
        return when (flag) {
            is EnvVar -> flag.enabled()
            else -> client.boolVariation(flag.key, ctx.toLDUser(), flag.default)
        }
    }
}

/**
 * Test feature-flag client. Intended only for usage in testing scenarios.
 *
 * All [Flag] instances will use the provided [values] map as their source of truth, including [EnvVar] flags.
 *
 * @param [values] is a map of [Flag.key] to enabled/disabled status.
 */
class TestClient(val values: Map<String, Boolean>) : FeatureFlagClient {
    override fun enabled(flag: Flag, ctx: Context): Boolean {
        return when (flag) {
            is EnvVar -> {
                // convert to a EnvVar flag with a custom fetcher that uses the [values] of this Test class
                // instead of fetching from the environment variables
                EnvVar(envVar = flag.key, default = flag.default, team = flag.team) {
                    values[flag.key]?.toString() ?: flag.default.toString()
                }.enabled()
            }

            else -> values[flag.key] ?: flag.default
        }
    }
}


/**
 * Data wrapper around OSS feature-flag configuration file.
 *
 * The file has the format of:
 * flags:
 *  - name: feature-one
 *    enabled: true
 *  - name: feature-two
 *    enabled: false
 */
private data class PlatformFlags(val flags: List<PlatformFlag>)

/**
 * Data wrapper around an individual flag read from the configuration file.
 */
private data class PlatformFlag(val name: String, val enabled: Boolean)


/** The yaml mapper is used for reading the feature-flag configuration file. */
private val yamlMapper = ObjectMapper(YAMLFactory()).registerKotlinModule()

/**
 * Reads a yaml configuration file, converting it into a map of flag name to flag configuration.
 *
 * @param [path] to yaml config file
 * @return map of feature-flag name to feature-flag config
 */
//private fun readConfig(path: Path): Map<String, OSSFlag> = yamlMapper.readValue<List<OSSFlag>>(path.toFile())
//    .associateBy { it.name }
private fun readConfig(path: Path): Map<String, PlatformFlag> = yamlMapper.readValue<PlatformFlags>(path.toFile())
    .let { it.flags }
    .associateBy { it.name }

/**
 * Monitors a [Path] for changes, calling [block] when a change is detected.
 *
 * @receiver Path
 * @param [block] function called anytime a change is detected on this [Path]
 */
private fun Path.onChange(block: () -> Unit) {
    val watcher = fileSystem.newWatchService()
    // The watcher services requires a directory to be provided, hence the `parent` reference here as `this` path should be a file.
    parent.register(watcher, StandardWatchEventKinds.ENTRY_MODIFY, StandardWatchEventKinds.ENTRY_CREATE)

    thread(isDaemon = true, name = "feature-flag-watcher", priority = MIN_PRIORITY) {
        val key = watcher.take()
        // The context on the poll-events for ENTRY_MODIFY events should not be null, this is a sanity check more than anything else
        key.pollEvents().mapNotNull { it.context() as? Path }
            .filter { this.endsWith(it) }
            .forEach { _ -> block() }

        key.reset()
    }
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
            user?.let { builder.set("user", it) }
        }

        is User -> Unit
    }
    return builder.build()
}