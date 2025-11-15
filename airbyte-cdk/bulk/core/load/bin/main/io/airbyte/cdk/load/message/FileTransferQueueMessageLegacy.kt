/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.message

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.state.CheckpointId

// DEPRECATED: Legacy file transfer
sealed interface FileTransferQueueMessage {
    val stream: DestinationStream
}

data class FileTransferQueueRecord(
    override val stream: DestinationStream,
    val file: DestinationFile,
    val index: Long,
    val checkpointId: CheckpointId
) : FileTransferQueueMessage

data class FileTransferQueueEndOfStream(
    override val stream: DestinationStream,
) : FileTransferQueueMessage
