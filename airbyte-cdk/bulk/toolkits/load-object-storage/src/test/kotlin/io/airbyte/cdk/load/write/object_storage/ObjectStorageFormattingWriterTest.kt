/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.write.object_storage

import io.airbyte.cdk.load.command.Append
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.command.NamespaceMapper
import io.airbyte.cdk.load.config.NamespaceDefinitionType
import io.airbyte.cdk.load.data.FieldType
import io.airbyte.cdk.load.data.ObjectType
import io.airbyte.cdk.load.data.StringType
import io.airbyte.cdk.load.file.NoopProcessor
import io.airbyte.cdk.load.file.object_storage.BufferedFormattingWriter
import io.airbyte.cdk.load.file.object_storage.JsonFormattingWriter
import io.airbyte.cdk.load.file.object_storage.ObjectStorageFormattingWriter
import io.airbyte.cdk.load.message.DestinationRecordJsonSource
import io.airbyte.cdk.load.message.DestinationRecordRaw
import io.airbyte.protocol.models.Jsons
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.AirbyteRecordMessage
import io.mockk.coEvery
import io.mockk.impl.annotations.MockK
import io.mockk.mockk
import java.io.ByteArrayOutputStream
import java.util.UUID
import kotlin.test.assertEquals
import org.junit.jupiter.api.Test

class ObjectStorageFormattingWriterTest {
    @MockK(relaxed = true) lateinit var underlyingWriter: ObjectStorageFormattingWriter

    @Test
    fun `buffered formatting writer never produces empty parts`() {
        val outputStream = ByteArrayOutputStream()
        outputStream.write("i am a header".toByteArray())
        val bufferedWriter =
            BufferedFormattingWriter(
                underlyingWriter,
                outputStream,
                NoopProcessor,
                NoopProcessor.wrapper(outputStream),
            )

        assert(bufferedWriter.bufferSize == 0) { "buffer appears empty despite header" }
        assert(bufferedWriter.takeBytes() == null) { "buffer yields no data despite header" }
        assert(bufferedWriter.finish() == null) { "buffer yields no data despite header" }
    }

    @Test
    fun `buffered formatting writer yields entire buffer once any data has been added`() {
        val outputStream = ByteArrayOutputStream()
        outputStream.write("i am a header".toByteArray())
        val bufferedWriter =
            BufferedFormattingWriter(
                underlyingWriter,
                outputStream,
                NoopProcessor,
                NoopProcessor.wrapper(outputStream),
            )

        assert(bufferedWriter.takeBytes() == null)
        coEvery { bufferedWriter.accept(any()) } coAnswers { outputStream.write("!".toByteArray()) }
        bufferedWriter.accept(mockk())
        val bytes = bufferedWriter.takeBytes()
        assert(bytes != null) { "buffer yields data now that we've written to it" }
        assert(bytes.contentEquals("i am a header!".toByteArray())) {
            "buffer yields all data written to it"
        }
    }
}

private val stream =
    DestinationStream(
        unmappedNamespace = "test_ns",
        unmappedName = "test_name",
        Append,
        ObjectType(linkedMapOf("foo" to FieldType(StringType, nullable = true))),
        generationId = 42,
        minimumGenerationId = 0,
        syncId = 123,
        namespaceMapper = NamespaceMapper(namespaceDefinitionType = NamespaceDefinitionType.SOURCE),
    )

private val record =
    DestinationRecordRaw(
        stream,
        DestinationRecordJsonSource(
            AirbyteMessage()
                .withType(AirbyteMessage.Type.RECORD)
                .withRecord(
                    AirbyteRecordMessage()
                        .withStream("test_name")
                        .withNamespace("test_ns")
                        .withEmittedAt(1234)
                        .withData(Jsons.deserialize("""{"foo": "bar"}"""))
                )
        ),
        serializedSizeBytes = 42,
        airbyteRawId = UUID.fromString("0197604b-ca2e-7e7c-9126-dacc18b68e8e"),
    )

class JsonFormattingWriterTest {
    @Test
    fun testAcceptNoFlattening() {
        val os = ByteArrayOutputStream()
        val writer = JsonFormattingWriter(stream, os, rootLevelFlattening = false)
        writer.accept(record)
        assertEquals(
            """
            {"_airbyte_raw_id":"0197604b-ca2e-7e7c-9126-dacc18b68e8e","_airbyte_extracted_at":1234,"_airbyte_meta":{"sync_id":123,"changes":[]},"_airbyte_generation_id":42,"_airbyte_data":{"foo":"bar"}}
            
            """.trimIndent(),
            os.toByteArray().decodeToString(),
        )
    }

    @Test
    fun testAcceptWithFlattening() {
        val os = ByteArrayOutputStream()
        val writer = JsonFormattingWriter(stream, os, rootLevelFlattening = true)
        writer.accept(record)
        assertEquals(
            """
            {"_airbyte_raw_id":"0197604b-ca2e-7e7c-9126-dacc18b68e8e","_airbyte_extracted_at":1234,"_airbyte_meta":{"sync_id":123,"changes":[]},"_airbyte_generation_id":42,"foo":"bar"}
            
            """.trimIndent(),
            os.toByteArray().decodeToString(),
        )
    }
}
