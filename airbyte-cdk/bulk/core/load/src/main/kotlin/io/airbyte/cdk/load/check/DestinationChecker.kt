/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.check

import io.airbyte.cdk.load.command.DestinationConfiguration

// TODO: Deprecate in favor if v2
interface DestinationChecker<C : DestinationConfiguration> {
    fun check(config: C)
    fun cleanup(config: C) {}
}
