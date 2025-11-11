/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.discoverer.operation

import io.airbyte.cdk.load.command.DestinationOperation

interface OperationProvider {
    fun get(): List<DestinationOperation>
}
