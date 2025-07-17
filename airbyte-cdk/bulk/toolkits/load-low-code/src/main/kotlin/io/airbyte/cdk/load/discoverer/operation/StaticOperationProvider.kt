/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.discoverer.operation

import io.airbyte.cdk.load.command.DestinationOperation
import io.airbyte.cdk.load.command.ImportType
import io.airbyte.cdk.load.data.AirbyteType

/** This class has not been used yet but shows why we structured OperationSupplier as we did */
class StaticOperationProvider(
    private val objectName: String,
    private val syncMode: ImportType,
    private val schema: AirbyteType,
    private val matchingKeys: List<List<String>>,
) : OperationProvider {
    override fun get(): List<DestinationOperation> {
        return listOf(
            DestinationOperation(
                objectName,
                syncMode,
                schema,
                matchingKeys,
            )
        )
    }
}
