/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.message.dlq

import io.airbyte.cdk.load.command.Append
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.command.NamespaceMapper
import io.airbyte.cdk.load.data.AirbyteValueProxy
import io.airbyte.cdk.load.data.ObjectTypeWithoutSchema
import io.airbyte.cdk.load.data.StringType
import io.airbyte.cdk.load.message.DestinationRecordJsonSource
import io.airbyte.cdk.load.message.DestinationRecordRaw
import io.airbyte.cdk.load.schema.model.ColumnSchema
import io.airbyte.cdk.load.schema.model.StreamTableSchema
import io.airbyte.cdk.load.schema.model.TableName
import io.airbyte.cdk.load.schema.model.TableNames
import io.airbyte.cdk.load.state.CheckpointId
import io.airbyte.protocol.models.Jsons
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.AirbyteRecordMessage
import java.util.UUID
import kotlin.test.assertEquals
import kotlin.test.assertNotNull
import kotlin.test.assertNull
import org.junit.jupiter.api.Test

class DlqRecordBuilderTest {
    @Test
    fun `toDlqRecord should replace the data`() {
        val initialRecord =
            DestinationRecordRaw(
                stream = defaultStream,
                rawData = DestinationRecordJsonSource(defaultRecordMessage),
                serializedSizeBytes = 123L,
                checkpointId = CheckpointId("myCheckPoint"),
                airbyteRawId = UUID.randomUUID(),
            )
        val record =
            initialRecord.toDlqRecord(
                mapOf("new" to "content"),
                keepOriginalFields = false,
            )

        val newFieldAccessor = AirbyteValueProxy.FieldAccessor(1, "new", StringType)

        assertEquals(
            """{"new":"content"}""",
            record.rawData.asJsonRecord(arrayOf(newFieldAccessor)).toString(),
        )
    }

    @Test
    fun `toDlqRecord should merge the data`() {
        val initialRecord =
            DestinationRecordRaw(
                stream = defaultStream,
                rawData = DestinationRecordJsonSource(defaultRecordMessage),
                serializedSizeBytes = 123L,
                checkpointId = CheckpointId("myCheckPoint"),
                airbyteRawId = UUID.randomUUID(),
            )
        val record =
            initialRecord.toDlqRecord(
                mapOf("new" to "content"),
                keepOriginalFields = true,
            )

        val newFieldAccessor = AirbyteValueProxy.FieldAccessor(1, "new", StringType)

        assertEquals(
            """{"test":"data","new":"content"}""",
            record.rawData.asJsonRecord(arrayOf(newFieldAccessor)).toString(),
        )
    }

    @Test
    fun `toDlqRecord should preserve the source record metadata`() {
        val initialRecord =
            DestinationRecordRaw(
                stream = defaultStream,
                rawData = DestinationRecordJsonSource(defaultRecordMessage),
                serializedSizeBytes = 123L,
                checkpointId = CheckpointId("myCheckPoint"),
                airbyteRawId = UUID.randomUUID(),
            )
        val record = initialRecord.toDlqRecord(mapOf())

        assertEquals(initialRecord.stream, record.stream)
        assertEquals(initialRecord.serializedSizeBytes, record.serializedSizeBytes)
        assertEquals(initialRecord.checkpointId, record.checkpointId)
        assertEquals(initialRecord.airbyteRawId, record.airbyteRawId)
    }

    @Test
    fun `newDlqRecord should fill in the blanks`() {
        val record = defaultStream.newDlqRecord(mapOf("brand" to "new"))

        val fieldAccessor = AirbyteValueProxy.FieldAccessor(1, "brand", StringType)
        assertEquals(
            """{"brand":"new"}""",
            record.rawData.asJsonRecord(arrayOf(fieldAccessor)).toString(),
        )

        assertEquals(defaultStream, record.stream)
        assertEquals(0, record.serializedSizeBytes)
        assertNull(record.checkpointId)
        assertNotNull(record.airbyteRawId)
    }

    private val defaultStream =
        DestinationStream(
            unmappedName = "name",
            unmappedNamespace = "namespace",
            importType = Append,
            schema = ObjectTypeWithoutSchema,
            generationId = 2,
            minimumGenerationId = 1,
            syncId = 27,
            namespaceMapper = NamespaceMapper(),
            tableSchema =
                StreamTableSchema(
                    columnSchema =
                        ColumnSchema(
                            inputSchema = mapOf(),
                            inputToFinalColumnNames = mapOf(),
                            finalSchema = mapOf(),
                        ),
                    importType = Append,
                    tableNames = TableNames(finalTableName = TableName("namespace", "test")),
                ),
        )

    private val defaultRecordMessage =
        AirbyteMessage()
            .withRecord(
                AirbyteRecordMessage()
                    .withData(Jsons.deserialize("""{"test":"data"}""""))
                    .withEmittedAt(System.currentTimeMillis())
            )
            .withType(AirbyteMessage.Type.RECORD)
}
