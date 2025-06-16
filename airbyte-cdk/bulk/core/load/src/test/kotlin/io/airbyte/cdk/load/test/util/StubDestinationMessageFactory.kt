/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.test.util

import com.fasterxml.jackson.databind.node.JsonNodeFactory
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.message.CheckpointMessage
import io.airbyte.cdk.load.message.DestinationFile
import io.airbyte.cdk.load.message.DestinationFileStreamComplete
import io.airbyte.cdk.load.message.DestinationRecord
import io.airbyte.cdk.load.message.DestinationRecordJsonSource
import io.airbyte.cdk.load.message.DestinationRecordStreamComplete
import io.airbyte.cdk.load.message.GlobalCheckpoint
import io.airbyte.cdk.load.message.StreamCheckpoint
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.AirbyteRecordMessage
import io.airbyte.protocol.models.v0.AirbyteStateMessage
import java.util.UUID

/*
 * Shared factory methods for making stub destination messages for testing.
 */
object StubDestinationMessageFactory {
    fun makeRecord(stream: DestinationStream): DestinationRecord {
        return DestinationRecord(
            stream = stream,
            message =
                DestinationRecordJsonSource(
                    AirbyteMessage()
                        .withRecord(
                            AirbyteRecordMessage().withData(JsonNodeFactory.instance.nullNode())
                        )
                ),
            serializedSizeBytes = 0L,
            airbyteRawId = UUID.randomUUID()
        )
    }

    fun makeFile(stream: DestinationStream): DestinationFile {
        return DestinationFile(
            stream = stream,
            emittedAtMs = 0,
            fileMessage = nullFileMessage,
        )
    }

    fun makeStreamComplete(stream: DestinationStream): DestinationRecordStreamComplete {
        return DestinationRecordStreamComplete(stream = stream, emittedAtMs = 0)
    }

    fun makeFileStreamComplete(stream: DestinationStream): DestinationFileStreamComplete {
        return DestinationFileStreamComplete(stream = stream, emittedAtMs = 0)
    }

    fun makeStreamState(stream: DestinationStream, recordCount: Long): CheckpointMessage {
        return StreamCheckpoint(
            checkpoint =
                CheckpointMessage.Checkpoint(
                    stream.descriptor,
                    JsonNodeFactory.instance.objectNode()
                ),
            sourceStats = CheckpointMessage.Stats(recordCount),
            serializedSizeBytes = 0L
        )
    }

    fun makeGlobalState(recordCount: Long): CheckpointMessage {
        return GlobalCheckpoint(
            state = JsonNodeFactory.instance.objectNode(),
            sourceStats = CheckpointMessage.Stats(recordCount),
            checkpoints = emptyList(),
            additionalProperties = emptyMap(),
            originalTypeField = AirbyteStateMessage.AirbyteStateType.GLOBAL,
            serializedSizeBytes = 0L
        )
    }

    private val nullFileMessage = DestinationFile.AirbyteRecordMessageFile()
}
