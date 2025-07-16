/*
 * Copyright (c) 2025 Airbyte, Inc.
 */
package io.airbyte.cdk.load.file.object_storage

import io.airbyte.cdk.load.command.object_storage.AvroFormatConfiguration
import io.airbyte.cdk.load.message.DestinationRecordProtobufSource
import io.airbyte.cdk.load.message.DestinationRecordRaw
import io.airbyte.cdk.load.message.DestinationRecordSource
import io.airbyte.protocol.protobuf.AirbyteMessage
import io.airbyte.protocol.protobuf.AirbyteRecordMessage
import io.mockk.every
import io.mockk.junit5.MockKExtension
import io.mockk.mockk
import java.io.ByteArrayOutputStream
import java.math.BigInteger
import org.apache.avro.file.CodecFactory
import org.apache.avro.file.DataFileReader
import org.apache.avro.file.SeekableByteArrayInput
import org.apache.avro.generic.GenericDatumReader
import org.apache.avro.generic.GenericRecord
import org.junit.jupiter.api.Assertions.*
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.extension.ExtendWith

@ExtendWith(MockKExtension::class)
class ProtoToAvroFormattingTest : ProtoFixtures(false) {

    private fun cfg(): AvroFormatConfiguration = mockk {
        every { avroCompressionConfiguration.compressionCodec } returns CodecFactory.nullCodec()
    }

    @Test
    fun `writes one Avro record with flattened columns`() {
        val out = ByteArrayOutputStream()
        val formatter = ProtoToAvroFormatter(stream, out, cfg(), rootLevelFlattening = true)

        formatter.accept(record)
        formatter.close()

        val reader =
            DataFileReader<GenericRecord>(
                SeekableByteArrayInput(out.toByteArray()),
                GenericDatumReader(),
            )
        assertTrue(reader.hasNext())
        val rec = reader.next()

        // meta
        assertEquals(uuid.toString(), rec.get("_airbyte_raw_id").toString())
        assertEquals(emittedAtMs, rec.get("_airbyte_extracted_at"))
        assertEquals(generationId, rec.get("_airbyte_generation_id"))

        // primitives
        assertEquals(true, rec["bool_col"])
        assertEquals(123L, rec["int_col"])
        assertEquals(12.34, rec["num_col"])
        assertEquals("hello", rec["string_col"].toString())
        assertEquals(20256, rec["date_col"])
        assertEquals(79199000000L, rec["time_tz_col"])
        assertEquals(86399000000L, rec["time_no_tz_col"])
        assertEquals(1750197599000000L, rec["ts_tz_col"])
        assertEquals(1750204799000000L, rec["ts_no_tz_col"])

        // complex
        assertEquals(listOf("a", "b"), (rec["array_col"] as List<*>).map { it.toString() })
        val obj = rec["obj_col"] as GenericRecord
        assertEquals("v", obj["k"].toString())
        val union = rec["union_col"] as GenericRecord
        assertEquals(1L, union["u"])

        // meta‑changes propagated
        val meta = rec["_airbyte_meta"] as GenericRecord
        val changes = meta["changes"] as List<*>
        assertEquals(3, changes.size)
        assertEquals("x", (changes[0] as GenericRecord)["field"].toString())
        assertEquals("NULLED", (changes[0] as GenericRecord)["change"].toString())
        assertEquals(
            "DESTINATION_SERIALIZATION_ERROR",
            (changes[0] as GenericRecord)["reason"].toString(),
        )
        assertEquals("y", (changes[1] as GenericRecord)["field"].toString())
        assertEquals("NULLED", (changes[1] as GenericRecord)["change"].toString())
        assertEquals(
            "SOURCE_SERIALIZATION_ERROR",
            (changes[1] as GenericRecord)["reason"].toString(),
        )
        assertEquals("z", (changes[2] as GenericRecord)["field"].toString())
        assertEquals("TRUNCATED", (changes[2] as GenericRecord)["change"].toString())
        assertEquals(
            "SOURCE_RECORD_SIZE_LIMITATION",
            (changes[2] as GenericRecord)["reason"].toString(),
        )
    }

    @Test
    fun `throws when formatter is constructed for non‑flatten mode`() {
        assertThrows(RuntimeException::class.java) {
            ProtoToAvroFormatter(
                stream,
                ByteArrayOutputStream(),
                cfg(),
                rootLevelFlattening = false,
            )
        }
    }

    @Test
    fun `throws when record is not protobuf`() {
        val nonProto =
            mockk<DestinationRecordRaw> {
                every { rawData } returns mockk<DestinationRecordSource>(relaxed = true)
            }

        val formatter = ProtoToAvroFormatter(stream, ByteArrayOutputStream(), cfg(), true)
        val ex = assertThrows(RuntimeException::class.java) { formatter.accept(nonProto) }
        assertTrue(ex.message!!.contains("expects DestinationRecordProtobufSource"))
    }

    @Test
    fun `integer beyond 64 bit is nulled`() {
        val big = BigInteger.valueOf(Long.MAX_VALUE).add(BigInteger.ONE)
        val patchedRecord = buildModifiedRecord(intBigInteger = big.toString())
        every { record.rawData } returns patchedRecord

        val ex =
            assertThrows(RuntimeException::class.java) {
                ProtoToAvroFormatter(stream, ByteArrayOutputStream(), cfg(), true).apply {
                    accept(record)
                    close()
                }
            }

        assertTrue(
            ex.message!!.contains(
                "java.lang.NullPointerException: null value for (non-nullable) long at dummy.int_col"
            )
        )
    }

    private fun buildModifiedRecord(
        intBigInteger: String? = null,
    ): DestinationRecordProtobufSource {
        val baseVals = protoSource!!.source.record.dataList.toMutableList()

        intBigInteger?.let {
            baseVals[1] =
                AirbyteRecordMessage.AirbyteValueProtobuf.newBuilder().setBigInteger(it).build()
        }

        val recProto =
            AirbyteRecordMessage.AirbyteRecordMessageProtobuf.newBuilder()
                .mergeFrom(protoSource!!.source.record)
                .clearData()
                .addAllData(baseVals)
                .build()

        val msg = AirbyteMessage.AirbyteMessageProtobuf.newBuilder().setRecord(recProto).build()

        return DestinationRecordProtobufSource(msg)
    }
}
