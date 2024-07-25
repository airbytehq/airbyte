/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.destination

import io.airbyte.protocol.models.v0.AirbyteStreamStatusTraceMessage.AirbyteStreamStatus

data class StreamSyncSummary(
    val recordsWritten: Long,
    val terminalStatus: AirbyteStreamStatus,
)
