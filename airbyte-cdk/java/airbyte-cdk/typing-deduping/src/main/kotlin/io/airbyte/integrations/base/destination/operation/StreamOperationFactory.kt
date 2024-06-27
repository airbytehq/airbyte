/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.base.destination.operation

import io.airbyte.integrations.base.destination.typing_deduping.DestinationInitialStatus

fun interface StreamOperationFactory<DestinationState> {

    /**
     * Create an instance with required dependencies injected using a concrete factory
     * implementation.
     */
    fun createInstance(
        destinationInitialStatus: DestinationInitialStatus<DestinationState>,
        disableTypeDedupe: Boolean,
    ): StreamOperation<DestinationState>
}
