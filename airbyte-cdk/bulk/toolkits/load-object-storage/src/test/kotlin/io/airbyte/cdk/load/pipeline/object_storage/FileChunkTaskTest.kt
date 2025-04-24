/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.pipeline.object_storage

import io.airbyte.cdk.load.command.Append
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.data.FieldType
import io.airbyte.cdk.load.data.ObjectType
import io.airbyte.cdk.load.data.StringType
import io.airbyte.cdk.load.message.DestinationRecordRaw
import io.airbyte.cdk.load.pipline.object_storage.file.FileChunkTask.Companion.COLUMN_NAME_AIRBYTE_FILE_PATH
import io.airbyte.cdk.load.pipline.object_storage.file.FileChunkTask.Companion.enrichRecordWithFilePath
import io.airbyte.protocol.models.Jsons
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.AirbyteRecordMessage
import kotlin.test.assertContains
import kotlin.test.assertEquals
import org.junit.jupiter.api.Test

class FileChunkTaskTest {
    @Test
    fun `enrichRecordsWithFilePath updates the schema and the corresponding data field`() {
        val message =
            AirbyteMessage()
                .withRecord(
                    AirbyteRecordMessage()
                        .withData(Jsons.deserialize("""{"something": "has to give"}"""))
                )
        val schema =
            ObjectType(
                properties =
                    LinkedHashMap(mapOf("something" to FieldType(StringType, nullable = true)))
            )
        val record =
            DestinationRecordRaw(
                stream =
                    DestinationStream(
                        descriptor = DestinationStream.Descriptor(null, "streamName"),
                        importType = Append,
                        generationId = 1,
                        minimumGenerationId = 0,
                        syncId = 3,
                        schema = schema,
                        includeFiles = true,
                    ),
                rawData = message,
                serialized = "",
                schema = schema,
            )
        val myFilePath = "proto://bucket/path/file"

        record.enrichRecordWithFilePath(myFilePath)

        assertEquals(
            FieldType(StringType, nullable = true),
            schema.properties[COLUMN_NAME_AIRBYTE_FILE_PATH]
        )
        assertContains(
            Jsons.serialize(record.asRawJson()),
            """"$COLUMN_NAME_AIRBYTE_FILE_PATH":"$myFilePath""""
        )
    }
}
