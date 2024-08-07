/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.configoss

import io.github.oshai.kotlinlogging.KotlinLogging
import java.util.*
import java.util.function.Function

private val LOGGER = KotlinLogging.logger {}

class EnvConfigs @JvmOverloads constructor(envMap: Map<String?, String?> = System.getenv()) :
    Configs {
    private val getEnv = Function { key: String -> envMap[key] }

    /**
     * Constructs [EnvConfigs] from a provided map. This can be used for testing or getting
     * variables from a non-envvar source.
     */
    override val specCacheBucket: String
        get() = getEnvOrDefault(SPEC_CACHE_BUCKET, DEFAULT_SPEC_CACHE_BUCKET)

    val localCatalogPath: Optional<String>
        get() = Optional.ofNullable(getEnv(LOCAL_CONNECTOR_CATALOG_PATH))

    // Worker - Data plane
    // Helpers
    fun getEnvOrDefault(key: String, defaultValue: String): String {
        return getEnvOrDefault(key, defaultValue, Function.identity(), false)
    }

    fun <T> getEnvOrDefault(
        key: String,
        defaultValue: T,
        parser: Function<String, T>,
        isSecret: Boolean
    ): T {
        val value = getEnv.apply(key)
        if (!value.isNullOrEmpty()) {
            return parser.apply(value)
        } else {
            LOGGER.info {
                "Using default value for environment variable $key: '${if (isSecret) "*****" else defaultValue.toString()}'"
            }
            return defaultValue
        }
    }

    fun getEnv(name: String): String? {
        return getEnv.apply(name)
    }

    companion object {

        // env variable names
        const val SPEC_CACHE_BUCKET: String = "SPEC_CACHE_BUCKET"
        const val LOCAL_CONNECTOR_CATALOG_PATH: String = "LOCAL_CONNECTOR_CATALOG_PATH"

        // defaults
        private const val DEFAULT_SPEC_CACHE_BUCKET = "io-airbyte-cloud-spec-cache"
    }
}
