/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.data.icerberg.parquet

import io.airbyte.cdk.load.test.util.ConfigurationUpdater
import io.airbyte.cdk.load.test.util.DefaultNamespaceResult

object IcebergConfigUpdater : ConfigurationUpdater {
    // TODO maybe we should replace our hardcoded config strings with this? unclear
    override fun update(config: String): String = config

    override fun setDefaultNamespace(
        config: String,
        defaultNamespace: String
    ): DefaultNamespaceResult =
        DefaultNamespaceResult(
            config.replace("<DEFAULT_NAMESPACE_PLACEHOLDER>", defaultNamespace),
            defaultNamespace
        )
}
