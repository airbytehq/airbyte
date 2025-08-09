/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.test.util

/** Utility that may update/modify a connector configuration for test purposes. */
interface ConfigurationUpdater {

    /**
     * May modify one or more entry in the provided configuration.
     * @param config The connector configuration.
     * @return The potentially modified configuration.
     */
    fun update(config: String): String

    /**
     * Some destinations have a concept of a "default namespace', which is used for streams with
     * `namespace = null`. For example, Bigquery's "default dataset", Postgres' "default schema".
     *
     * This function should return a copy of the config, but updated with the default namespace as
     * [defaultNamespace].
     */
    fun setDefaultNamespace(config: String, defaultNamespace: String): DefaultNamespaceResult
}

data class DefaultNamespaceResult(val updatedConfig: String, val actualDefaultNamespace: String?)

/**
 * Basic implementation of the [ConfigurationUpdater] interface that does not modify the
 * configuration.
 */
object FakeConfigurationUpdater : ConfigurationUpdater {
    override fun update(config: String): String = config
    override fun setDefaultNamespace(
        config: String,
        defaultNamespace: String
    ): DefaultNamespaceResult = DefaultNamespaceResult(config, null)
}
