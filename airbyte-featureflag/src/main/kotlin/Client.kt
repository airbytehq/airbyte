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
import io.micronaut.context.annotation.Property
import io.micronaut.context.annotation.Requires
import jakarta.inject.Singleton
import java.lang.Thread.MIN_PRIORITY
import java.nio.file.Path
import java.nio.file.StandardWatchEventKinds
import java.nio.file.WatchService
import java.util.concurrent.locks.ReentrantReadWriteLock
import kotlin.concurrent.read
import kotlin.concurrent.thread
import kotlin.concurrent.write
import kotlin.io.path.isRegularFile

/**
 * Feature-Flag Client interface.
 */
sealed interface FeatureFlagClient {
    /**
     * Returns true if the flag with the provided context should be enabled. Returns false otherwise.
     */
    fun enabled(flag: Flag, ctx: Context): Boolean
}

/** Config key used to determine which [FeatureFlagClient] to expose. */
internal const val CONFIG_FF_CLIENT = "airbyte.feature-flag.client"

/** If [CONFIG_FF_CLIENT] equals this value, return the [LaunchDarklyClient], otherwise the [ConfigFileClient]. */
internal const val CONFIG_FF_CLIENT_VAL_LAUNCHDARKLY = "launchdarkly"

/** Config key to provide the api-key as required by the [LaunchDarklyClient]. */
internal const val CONFIG_FF_APIKEY = "airbyte.feature-flag.api-key"

/** Config key to provided the location of the flags config file used by the [ConfigFileClient]. */
internal const val CONFIG_FF_PATH = "airbyte.feature-flag.path"

/**
 * Config file based feature-flag client.
 *
 * If no [config] is provided, will return the default state for each [Flag] requested.
 * Supports [EnvVar] flags as well.
 *
 * @param [config] optional location of the yaml config file that contains the feature-flag definitions.
 * If the [config] is provided, it will be watched for changes and the internal representation of the [config] will be updated to match.
 */
@Singleton
@Requires(property = CONFIG_FF_CLIENT, notEquals = CONFIG_FF_CLIENT_VAL_LAUNCHDARKLY)
class ConfigFileClient(@Property(name = CONFIG_FF_PATH) config: Path?) : FeatureFlagClient {
    /** [flags] holds the mappings of the flag-name to the flag properties */
    private var flags: Map<String, ConfigFileFlag> = config?.let { readConfig(it) } ?: mapOf()

    /** lock is used for ensuring access to the flags map is handled correctly when the map is being updated. */
    private val lock = ReentrantReadWriteLock()

    init {
        config?.also {
            if (!it.isRegularFile()) {
                throw IllegalArgumentException("config must reference a file")
            }

            it.onChange {
                lock.write { flags = readConfig(config) }
            }
        }
    }

    override fun enabled(flag: Flag, ctx: Context): Boolean {
        return when (flag) {
            is EnvVar -> flag.enabled(ctx)
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
@Singleton
@Requires(property = CONFIG_FF_CLIENT, value = CONFIG_FF_CLIENT_VAL_LAUNCHDARKLY)
class LaunchDarklyClient(private val client: LDClient) : FeatureFlagClient {
    override fun enabled(flag: Flag, ctx: Context): Boolean {
        return when (flag) {
            is EnvVar -> flag.enabled(ctx)
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
class TestClient @JvmOverloads constructor(val values: Map<String, Boolean> = mapOf()) : FeatureFlagClient {
    override fun enabled(flag: Flag, ctx: Context): Boolean {
        return when (flag) {
            is EnvVar -> {
                // convert to a EnvVar flag with a custom fetcher that uses the [values] of this Test class
                // instead of fetching from the environment variables
                EnvVar(envVar = flag.key, default = flag.default, attrs = flag.attrs).apply {
                    fetcher = { values[flag.key]?.toString() ?: flag.default.toString() }
                }.enabled(ctx)
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
private data class ConfigFileFlags(val flags: List<ConfigFileFlag>)

/**
 * Data wrapper around an individual flag read from the configuration file.
 */
private data class ConfigFileFlag(val name: String, val enabled: Boolean)


/** The yaml mapper is used for reading the feature-flag configuration file. */
private val yamlMapper = ObjectMapper(YAMLFactory()).registerKotlinModule()

/**
 * Reads a yaml configuration file, converting it into a map of flag name to flag configuration.
 *
 * @param [path] to yaml config file
 * @return map of feature-flag name to feature-flag config
 */
private fun readConfig(path: Path): Map<String, ConfigFileFlag> = yamlMapper.readValue<ConfigFileFlags>(path.toFile()).flags
    .associateBy { it.name }

/**
 * Monitors a [Path] for changes, calling [block] when a change is detected.
 *
 * @receiver Path
 * @param [block] function called anytime a change is detected on this [Path]
 */
private fun Path.onChange(block: () -> Unit) {
    val watcher: WatchService = fileSystem.newWatchService()
    // The watcher service requires a directory to be registered and not an individual file. This Path is an individual file,
    // hence the `parent` reference to register the parent of this file (which is the directory that contains this file).
    // As all files within this directory could send events, any file that doesn't match this Path will need to be filtered out.
    parent.register(watcher, StandardWatchEventKinds.ENTRY_MODIFY, StandardWatchEventKinds.ENTRY_CREATE)

    thread(isDaemon = true, name = "feature-flag-watcher", priority = MIN_PRIORITY) {
        val key = watcher.take()
        // The context on the poll-events for ENTRY_MODIFY and ENTRY_CREATE events should return a Path,
        // however officially `Returns: the event context; may be null`, so there is a null check here
        key.pollEvents().mapNotNull { it.context() as? Path }
            // As events are generated at the directory level and not the file level, any files that do not match the specific file
            // this Path represents must be filtered out.
            // E.g.
            // If this path is "/tmp/dir/flags.yml",
            // the directory registered with the WatchService was "/tmp/dir",
            // and the event's path would be "flags.yml".
            //
            // This filter verifies that "/tmp/dir/flags.yml" ends with "flags.yml" before calling the block method.
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
private fun Context.toLDUser(): LDUser = when (this) {
    is Multi -> {
        val builder = LDUser.Builder(key)
        with(contexts) {
            // Add each individual context's value as an attribute on the LDUser.
            // This allows for more granular targeting of feature-flag rules that target LDUser types.
            forEach { builder.custom(it.kind, it.key) }

            if (all { it.key == ANONYMOUS.toString() }) {
                builder.anonymous(true)
            }
        }
        builder.build()
    }

    else -> {
        // for LDv5 Users, add the context type and valid as a custom attribute
        val builder = LDUser.Builder(key).apply { custom(kind, key) }
        if (this.key == ANONYMOUS.toString()) {
            builder.anonymous(true)
        }
        builder.build()
    }
}

/**
 * LaunchDarkly v6 version
 *
 * Replaces toLDUser once LaunchDarkly v6 is GA.
 */
private fun Context.toLDContext(): LDContext {
    if (this is Multi) {
        val builder = LDContext.multiBuilder()
        contexts.forEach { builder.add(it.toLDContext()) }
        return builder.build()
    }

    val builder = LDContext.builder(ContextKind.of(kind), key)
    if (key == ANONYMOUS.toString()) {
        builder.anonymous(true)
    }

    when (this) {
        is Workspace -> user?.let { builder.set("user", it) }
        else -> Unit
    }

    return builder.build()
}
