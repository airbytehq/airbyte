/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.base.destination.typing_deduping

@JvmRecord
data class DestinationInitialStatus<DestinationState>(
    val streamConfig: StreamConfig,
    val isFinalTablePresent: Boolean,
    // TODO we should probably make this nullable, then delete InitialRawTableStatus.rawTableExists
    val initialRawTableStatus: InitialRawTableStatus,
    /**
     * The state of the temp raw table, or null if there is no temp raw table at the start of the
     * sync.
     */
    val initialTempRawTableStatus: InitialRawTableStatus,
    val isSchemaMismatch: Boolean,
    val isFinalTableEmpty: Boolean,
    val destinationState: DestinationState,
)
