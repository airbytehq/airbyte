/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mssql.v2

import io.airbyte.cdk.load.test.util.ConfigurationUpdater
import io.airbyte.cdk.load.test.util.DefaultNamespaceResult

class BulkInsertConfigUpdater : ConfigurationUpdater {

    private val delegate = MSSQLConfigUpdater()

    override fun update(config: String): String {
        return delegate.update(config)
    }

    override fun setDefaultNamespace(
        config: String,
        defaultNamespace: String
    ): DefaultNamespaceResult = delegate.setDefaultNamespace(config, defaultNamespace)
}
