/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.checker

import io.airbyte.cdk.load.check.DestinationChecker
import io.airbyte.cdk.load.check.dlq.DlqChecker
import io.airbyte.cdk.load.command.DestinationConfiguration
import io.airbyte.cdk.load.command.dlq.ObjectStorageConfigProvider

class CompositeDlqChecker<C>(
    private val decorated: DestinationChecker<C>,
    private val dlqChecker: DlqChecker
) : DestinationChecker<C> where C : DestinationConfiguration, C : ObjectStorageConfigProvider {
    override fun check(config: C) {
        decorated.check(config)
        dlqChecker.check(config.objectStorageConfig)
    }
}
