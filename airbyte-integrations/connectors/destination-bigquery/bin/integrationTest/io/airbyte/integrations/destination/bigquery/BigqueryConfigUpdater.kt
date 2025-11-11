/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery

import io.airbyte.cdk.load.test.util.ConfigurationUpdater
import io.airbyte.cdk.load.test.util.DefaultNamespaceResult

const val DEFAULT_NAMESPACE_PLACEHOLDER = "DEFAULT_NAMESPACE_PLACEHOLDER"

object BigqueryConfigUpdater : ConfigurationUpdater {
    override fun update(config: String): String = config

    override fun setDefaultNamespace(
        config: String,
        defaultNamespace: String
    ): DefaultNamespaceResult =
        DefaultNamespaceResult(
            config.replace(DEFAULT_NAMESPACE_PLACEHOLDER, defaultNamespace),
            defaultNamespace
        )
}
