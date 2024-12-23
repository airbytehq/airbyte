/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.test.util

import com.fasterxml.jackson.databind.node.JsonNodeFactory
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.data.ObjectTypeWithoutSchema
import io.airbyte.cdk.load.message.CheckpointMessage
import io.airbyte.cdk.load.message.DestinationFile
import io.airbyte.cdk.load.message.DestinationFileStreamComplete
import io.airbyte.cdk.load.message.DestinationFileStreamIncomplete
import io.airbyte.cdk.load.message.DestinationRecord
import io.airbyte.cdk.load.message.DestinationRecordStreamComplete
import io.airbyte.cdk.load.message.DestinationRecordStreamIncomplete
import io.airbyte.cdk.load.message.GlobalCheckpoint
import io.airbyte.cdk.load.message.StreamCheckpoint
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.AirbyteRecordMessage
import io.airbyte.protocol.models.v0.AirbyteStateMessage

/*
 * Shared factory methods for making stub destination messages for testing.
 */
object StubDestinationMessageFactory {
    fun makeRecord(stream: DestinationStream): DestinationRecord {
        return DestinationRecord(
            stream = stream.descriptor,
            message =
                AirbyteMessage()
                    .withRecord(
                        AirbyteRecordMessage().withData(JsonNodeFactory.instance.nullNode())
                    ),
            serialized = "",
            schema = ObjectTypeWithoutSchema
        )
    }

    fun makeFile(stream: DestinationStream, record: String): DestinationFile {
        return DestinationFile(
            stream = stream.descriptor,
            emittedAtMs = 0,
            serialized = record,
            fileMessage = nullFileMessage,
        )
    }

    fun makeStreamComplete(stream: DestinationStream): DestinationRecordStreamComplete {
        return DestinationRecordStreamComplete(stream = stream.descriptor, emittedAtMs = 0)
    }

    fun makeFileStreamComplete(stream: DestinationStream): DestinationFileStreamComplete {
        return DestinationFileStreamComplete(stream = stream.descriptor, emittedAtMs = 0)
    }

    fun makeStreamIncomplete(stream: DestinationStream): DestinationRecordStreamIncomplete {
        return DestinationRecordStreamIncomplete(stream = stream.descriptor, emittedAtMs = 0)
    }

    fun makeFileStreamIncomplete(stream: DestinationStream): DestinationFileStreamIncomplete {
        return DestinationFileStreamIncomplete(stream = stream.descriptor, emittedAtMs = 0)
    }

    fun makeStreamState(stream: DestinationStream, recordCount: Long): CheckpointMessage {
        return StreamCheckpoint(
            checkpoint =
                CheckpointMessage.Checkpoint(
                    stream.descriptor,
                    JsonNodeFactory.instance.objectNode()
                ),
            sourceStats = CheckpointMessage.Stats(recordCount),
        )
    }

    fun makeGlobalState(recordCount: Long): CheckpointMessage {
        return GlobalCheckpoint(
            state = JsonNodeFactory.instance.objectNode(),
            sourceStats = CheckpointMessage.Stats(recordCount),
            checkpoints = emptyList(),
            additionalProperties = emptyMap(),
            originalTypeField = AirbyteStateMessage.AirbyteStateType.GLOBAL,
        )
    }

    private val nullFileMessage = DestinationFile.AirbyteRecordMessageFile()
}
