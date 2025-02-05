/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3_data_lake

import io.airbyte.cdk.load.test.util.ConfigurationUpdater

object S3DataLakeConfigUpdater : ConfigurationUpdater {
    // TODO maybe we should replace our hardcoded config strings with this? unclear
    override fun update(config: String): String = config

    override fun setDefaultNamespace(config: String, defaultNamespace: String): String {
        return config.replace("<DEFAULT_NAMESPACE_PLACEHOLDER>", defaultNamespace)
    }
}
