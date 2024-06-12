/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.base.destination.typing_deduping

import io.airbyte.protocol.models.v0.DestinationSyncMode
import java.util.*
import kotlin.collections.LinkedHashMap

data class StreamConfig(
    val id: StreamId,
    val destinationSyncMode: DestinationSyncMode,
    val primaryKey: List<ColumnId>,
    val cursor: Optional<ColumnId>,
    val columns: LinkedHashMap<ColumnId, AirbyteType>,
    val generationId: Long,
    val minimumGenerationId: Long,
    val syncId: Long,
)
