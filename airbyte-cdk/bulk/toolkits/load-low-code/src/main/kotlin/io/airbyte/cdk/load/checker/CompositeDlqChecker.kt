/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.checker

import io.airbyte.cdk.load.check.DestinationCheckerWithoutGeneric
import io.airbyte.cdk.load.check.dlq.DlqChecker
import io.airbyte.cdk.load.command.dlq.ObjectStorageConfig

class CompositeDlqChecker(
    private val decorated: DestinationCheckerWithoutGeneric,
    private val dlqChecker: DlqChecker,
    private val objectStorageConfig: ObjectStorageConfig
) : DestinationCheckerWithoutGeneric {
    override fun check() {
        decorated.check()
        dlqChecker.check(objectStorageConfig)
    }

    override fun cleanup() {
        decorated.cleanup()
    }
}
