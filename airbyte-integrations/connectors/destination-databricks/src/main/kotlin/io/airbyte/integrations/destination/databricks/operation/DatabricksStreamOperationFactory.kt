/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.databricks.operation

import io.airbyte.cdk.integrations.destination.s3.FileUploadFormat
import io.airbyte.integrations.base.destination.operation.StreamOperation
import io.airbyte.integrations.base.destination.operation.StreamOperationFactory
import io.airbyte.integrations.base.destination.typing_deduping.DestinationInitialStatus
import io.airbyte.integrations.base.destination.typing_deduping.migrators.MinimumDestinationState

class DatabricksStreamOperationFactory(private val storageOperations: DatabricksStorageOperation) :
    StreamOperationFactory<MinimumDestinationState.Impl> {
    override fun createInstance(
        destinationInitialStatus: DestinationInitialStatus<MinimumDestinationState.Impl>,
        disableTypeDedupe: Boolean,
    ): StreamOperation<MinimumDestinationState.Impl> {
        return DatabricksStreamOperation(
            storageOperations,
            destinationInitialStatus,
            FileUploadFormat.CSV,
            disableTypeDedupe,
        )
    }
}
