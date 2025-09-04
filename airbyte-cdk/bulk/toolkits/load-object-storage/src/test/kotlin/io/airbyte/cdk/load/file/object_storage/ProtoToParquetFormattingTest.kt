/*
 * Copyright (c) 2025 Airbyte, Inc.
 */
package io.airbyte.cdk.load.file.object_storage

import com.google.protobuf.kotlin.toByteString
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.command.computeUnknownColumnChanges
import io.airbyte.cdk.load.command.object_storage.ParquetFormatConfiguration
import io.airbyte.cdk.load.data.*
import io.airbyte.cdk.load.message.DestinationRecordProtobufSource
import io.airbyte.cdk.load.message.DestinationRecordRaw
import io.airbyte.cdk.load.message.DestinationRecordSource
import io.airbyte.protocol.protobuf.AirbyteMessage
import io.airbyte.protocol.protobuf.AirbyteRecordMessage
import io.mockk.every
import io.mockk.junit5.MockKExtension
import io.mockk.mockk
import java.io.ByteArrayInputStream
import java.io.ByteArrayOutputStream
import java.math.BigInteger
import org.apache.avro.generic.GenericRecord
import org.apache.parquet.avro.AvroParquetReader
import org.apache.parquet.io.DelegatingSeekableInputStream
import org.apache.parquet.io.InputFile
import org.apache.parquet.io.SeekableInputStream
import org.junit.jupiter.api.Assertions.*
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.extension.ExtendWith

@ExtendWith(MockKExtension::class)
class ProtoToParquetFormattingTest : ProtoFixtures(addUnknownTypeToSchema = false) {

    private fun cfg(): ParquetFormatConfiguration = mockk {
        every { parquetWriterConfiguration } returns
            io.airbyte.cdk.load.file.parquet.ParquetWriterConfiguration(
                compressionCodecName = "UNCOMPRESSED",
                blockSizeMb = 1,
                maxPaddingSizeMb = 1,
                pageSizeKb = 8,
                dictionaryPageSizeKb = 8,
                dictionaryEncoding = false,
            )
    }

    @Test
    fun `writes one Parquet record with flattened columns`() {
        val out = ByteArrayOutputStream()
        val formatter = ProtoToParquetFormatter(stream, out, cfg(), rootLevelFlattening = true)

        formatter.accept(record)
        formatter.close()

        val rec = readParquet(out.toByteArray()).single()

        assertEquals(uuid.toString(), rec.get("_airbyte_raw_id").toString())
        assertEquals(emittedAtMs, rec.get("_airbyte_extracted_at"))
        assertEquals(generationId, rec.get("_airbyte_generation_id"))

        assertEquals(true, rec["bool_col"])
        assertEquals(123L, rec["int_col"])
        assertEquals(12.34, rec["num_col"])
        assertEquals("hello", rec["string_col"].toString())
        assertEquals(20256, rec["date_col"])
        assertEquals(79199000000L, rec["time_tz_col"])
        assertEquals(86399000000L, rec["time_no_tz_col"])
        assertEquals(1750197599000000L, rec["ts_tz_col"])
        assertEquals(1750204799000000L, rec["ts_no_tz_col"])

        val arr = rec["array_col"] as List<*>
        assertEquals(listOf("a", "b"), arr.map { it.toString() })

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
    fun `disjoint union encodes object branch`() {
        patchSchemaAndAccessorsWithDuCol()

        val duObject = """{"u":1}"""
        every { record.rawData } returns buildRecordWithDuCol(duObject)

        val out = ByteArrayOutputStream()
        val formatter = ProtoToParquetFormatter(stream, out, cfg(), rootLevelFlattening = true)
        formatter.accept(record)
        formatter.close()

        val rec = readParquet(out.toByteArray()).single()

        val du = rec["du_col"] as GenericRecord
        assertEquals("object", du["type"].toString())
        val duObj = du["object"] as GenericRecord
        assertEquals(1L, duObj["u"])
        assertNull(du["string"])
    }

    @Test
    fun `disjoint union encodes string branch`() {
        patchSchemaAndAccessorsWithDuCol()

        val duString = "\"hello\""
        every { record.rawData } returns buildRecordWithDuCol(duString)

        val out = ByteArrayOutputStream()
        val formatter = ProtoToParquetFormatter(stream, out, cfg(), rootLevelFlattening = true)
        formatter.accept(record)
        formatter.close()

        val rec = readParquet(out.toByteArray()).single()

        val du = rec["du_col"] as GenericRecord
        assertEquals("string", du["type"].toString())
        assertEquals("hello", du["string"].toString())
        assertNull(du["object"])
    }

    @Test
    fun `throws when constructed for non-flatten mode`() {
        assertThrows(RuntimeException::class.java) {
            ProtoToParquetFormatter(
                stream,
                ByteArrayOutputStream(),
                cfg(),
                rootLevelFlattening = false
            )
        }
    }

    @Test
    fun `throws when record is not protobuf`() {
        val nonProto =
            mockk<DestinationRecordRaw> {
                every { rawData } returns mockk<DestinationRecordSource>(relaxed = true)
            }

        val formatter = ProtoToParquetFormatter(stream, ByteArrayOutputStream(), cfg(), true)
        val ex = assertThrows(RuntimeException::class.java) { formatter.accept(nonProto) }
        assertTrue(ex.message!!.contains("expects DestinationRecordProtobufSource"))
    }

    @Test
    fun `integer beyond 64 bit is nulled and Parquet write fails on non-nullable`() {
        val big = BigInteger.valueOf(Long.MAX_VALUE).add(BigInteger.ONE)
        every { record.rawData } returns buildModifiedRecord(intBigInteger = big.toString())

        val formatter = ProtoToParquetFormatter(stream, ByteArrayOutputStream(), cfg(), true)
        val ex =
            assertThrows(RuntimeException::class.java) {
                formatter.accept(record)
                formatter.close()
            }
        assertTrue(ex.message!!.contains("Null-value for required field: int_col"))
    }

    private fun patchSchemaAndAccessorsWithDuCol() {
        val currentSchema = stream.schema as ObjectType
        val duSchema =
            UnionType.of(ObjectType(linkedMapOf("u" to FieldType(IntegerType, false))), StringType)
        val newProps = LinkedHashMap(currentSchema.properties)
        newProps["du_col"] = FieldType(duSchema, false)
        val patched = ObjectType(newProps)

        val newAccessor =
            mockk<AirbyteValueProxy.FieldAccessor> {
                every { name } returns "du_col"
                every { type } returns duSchema
                try {
                    every { index } returns 12
                } catch (_: Exception) {}
            }
        val extended = fieldAccessors.toMutableList().apply { add(newAccessor) }.toTypedArray()

        every { stream.schema } returns patched
        every { stream.airbyteValueProxyFieldAccessors } returns extended
        every { stream.unknownColumnChanges } returns patched.computeUnknownColumnChanges()
        every { stream.mappedDescriptor } returns DestinationStream.Descriptor("", "dummy")
    }

    private fun buildRecordWithDuCol(jsonForDu: String): DestinationRecordProtobufSource {
        val base = protoSource!!.source.record.dataList.toMutableList()
        base.add(
            AirbyteRecordMessage.AirbyteValueProtobuf.newBuilder()
                .setJson(jsonForDu.toByteArray().toByteString())
                .build()
        )

        val recProto =
            AirbyteRecordMessage.AirbyteRecordMessageProtobuf.newBuilder()
                .mergeFrom(protoSource!!.source.record)
                .clearData()
                .addAllData(base)
                .build()

        val msg = AirbyteMessage.AirbyteMessageProtobuf.newBuilder().setRecord(recProto).build()
        return DestinationRecordProtobufSource(msg)
    }

    private fun buildModifiedRecord(
        intBigInteger: String? = null
    ): DestinationRecordProtobufSource {
        val base = protoSource!!.source.record.dataList.toMutableList()

        intBigInteger?.let {
            base[1] =
                AirbyteRecordMessage.AirbyteValueProtobuf.newBuilder().setBigInteger(it).build()
        }

        val recProto =
            AirbyteRecordMessage.AirbyteRecordMessageProtobuf.newBuilder()
                .mergeFrom(protoSource!!.source.record)
                .clearData()
                .addAllData(base)
                .build()

        val msg = AirbyteMessage.AirbyteMessageProtobuf.newBuilder().setRecord(recProto).build()
        return DestinationRecordProtobufSource(msg)
    }

    private fun readParquet(bytes: ByteArray): List<GenericRecord> {
        val input = ByteArrayInputFile(bytes)
        val reader = AvroParquetReader.builder<GenericRecord>(input).build()
        val out = mutableListOf<GenericRecord>()
        while (true) {
            val rec = reader.read() ?: break
            out += rec
        }
        reader.close()
        return out
    }

    private class ByteArrayInputFile(private val data: ByteArray) : InputFile {
        override fun getLength(): Long = data.size.toLong()
        override fun newStream(): SeekableInputStream {
            val bais = ByteArrayInputStream(data)
            var pos = 0L
            return object : DelegatingSeekableInputStream(bais) {
                override fun read(): Int {
                    val r = super.read()
                    if (r >= 0) pos++
                    return r
                }
                override fun read(b: ByteArray, off: Int, len: Int): Int {
                    val n = super.read(b, off, len)
                    if (n > 0) pos += n
                    return n
                }
                override fun getPos(): Long = pos
                override fun seek(newPos: Long) {
                    require(newPos >= 0 && newPos <= data.size) { "bad seek" }
                    bais.reset()
                    bais.skip(newPos)
                    pos = newPos
                }
            }
        }
    }
}
