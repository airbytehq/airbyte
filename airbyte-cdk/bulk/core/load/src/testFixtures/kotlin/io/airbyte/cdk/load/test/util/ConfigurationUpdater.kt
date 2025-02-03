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
}

/**
 * Basic implementation of the [ConfigurationUpdater] interface that does not modify the
 * configuration.
 */
object FakeConfigurationUpdater : ConfigurationUpdater {
    override fun update(config: String): String = config
}
