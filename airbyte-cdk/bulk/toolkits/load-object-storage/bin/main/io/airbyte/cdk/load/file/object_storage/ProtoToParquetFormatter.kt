/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.load.file.object_storage

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.command.object_storage.ParquetFormatConfiguration
import io.airbyte.cdk.load.data.*
import io.airbyte.cdk.load.data.avro.toAvroSchema
import io.airbyte.cdk.load.data.collectUnknownPaths
import io.airbyte.cdk.load.data.withAirbyteMeta
import io.airbyte.cdk.load.file.parquet.toParquetWriter
import io.airbyte.cdk.load.message.DestinationRecordProtobufSource
import io.airbyte.cdk.load.message.DestinationRecordRaw
import io.airbyte.cdk.load.message.Meta
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMetaChange
import java.io.OutputStream
import java.time.LocalDate
import java.time.LocalDateTime
import java.time.LocalTime
import java.time.OffsetDateTime
import java.time.OffsetTime
import java.time.ZoneOffset
import java.time.temporal.ChronoUnit
import org.apache.avro.Schema
import org.apache.avro.generic.GenericData
import org.apache.avro.generic.GenericRecord

class ProtoToParquetFormatter(
    private val stream: DestinationStream,
    outputStream: OutputStream,
    formatConfig: ParquetFormatConfiguration,
    private val rootLevelFlattening: Boolean,
) : ObjectStorageFormattingWriter {

    private val longMin = Long.MIN_VALUE.toBigInteger()
    private val longMax = Long.MAX_VALUE.toBigInteger()

    private val logicalSchema: ObjectType =
        unionToDisjointRecord(mergeUnions(stream.schema)).withAirbyteMeta(rootLevelFlattening)
    private val avroSchema: Schema = logicalSchema.toAvroSchema(stream.mappedDescriptor)
    private val writer =
        outputStream.toParquetWriter(avroSchema, formatConfig.parquetWriterConfiguration)

    private fun safe(name: String) = Transformations.toAvroSafeName(name)

    private val metaSchema = avroSchema.nonNullSubSchemaOf(safe(Meta.COLUMN_NAME_AB_META))
    private val changeArraySchema = metaSchema.getField("changes").schema().nonNullOrSelf()
    private val changeRecordSchema = changeArraySchema.elementType.nonNullOrSelf()

    private data class ColumnWriter(
        val fieldName: String,
        val accessor: AirbyteValueProxy.FieldAccessor,
        val avroSubSchema: Schema,
        val write: (GenericRecord, AirbyteValueProxy, MutableList<Meta.Change>) -> Unit,
    )

    private val colWriters: List<ColumnWriter> = buildColumnWriters()

    private val unknownColumns = stream.schema.collectUnknownPaths()

    init {
        if (unknownColumns.isNotEmpty()) {
            throw RuntimeException(
                "Unknown columns $unknownColumns encountered for stream ${stream.mappedDescriptor}"
            )
        }
        if (!rootLevelFlattening) {
            throw RuntimeException("Parquet format doesn't support non-flattening mode")
        }
    }

    override fun accept(record: DestinationRecordRaw) {
        val src =
            record.rawData as? DestinationRecordProtobufSource
                ?: error("expects DestinationRecordProtobufSource")

        val proxy = src.asAirbyteValueProxy()
        val errors = mutableListOf<Meta.Change>()
        val root = GenericData.Record(avroSchema)

        root.put(Meta.COLUMN_NAME_AB_RAW_ID, record.airbyteRawId.toString())
        root.put(Meta.COLUMN_NAME_AB_EXTRACTED_AT, src.emittedAtMs)
        root.put(Meta.COLUMN_NAME_AB_GENERATION_ID, record.stream.generationId)

        if (rootLevelFlattening) {
            colWriters.forEach { it.write(root, proxy, errors) }
        } else {
            throw RuntimeException("Parquet format doesn't support non-flattening mode")
        }

        root.put(
            Meta.COLUMN_NAME_AB_META,
            buildMeta(record.stream.syncId, src.sourceMeta.changes + errors),
        )

        writer.write(root)
    }

    override fun flush() = Unit
    override fun close() = writer.close()

    private fun buildColumnWriters(): List<ColumnWriter> {
        val accessors = stream.airbyteValueProxyFieldAccessors
        return accessors.map { acc ->
            val (subSchema, fieldName) =
                if (rootLevelFlattening) {
                    val n = safe(acc.name)
                    avroSchema.getField(n).schema().nonNullOrSelf() to n
                } else {
                    throw RuntimeException("Parquet format doesn't support non-flattening mode")
                }

            fun addError(ch: MutableList<Meta.Change>) =
                ch.add(
                    Meta.Change(
                        acc.name,
                        AirbyteRecordMessageMetaChange.Change.NULLED,
                        AirbyteRecordMessageMetaChange.Reason.DESTINATION_SERIALIZATION_ERROR,
                    ),
                )

            val writer: (GenericRecord, AirbyteValueProxy, MutableList<Meta.Change>) -> Unit =
                when (acc.type) {
                    is BooleanType -> { rec, p, _ -> rec.put(fieldName, p.getBoolean(acc)) }
                    is IntegerType -> { rec, p, ch ->
                            p.getInteger(acc)?.let { v ->
                                if (v in longMin..longMax) rec.put(fieldName, v.toLong())
                                else {
                                    rec.put(fieldName, null)
                                    ch.add(
                                        Meta.Change(
                                            acc.name,
                                            AirbyteRecordMessageMetaChange.Change.NULLED,
                                            AirbyteRecordMessageMetaChange.Reason
                                                .DESTINATION_FIELD_SIZE_LIMITATION,
                                        ),
                                    )
                                }
                            }
                        }
                    is NumberType -> { rec, p, _ ->
                            p.getNumber(acc)?.toDouble()?.let { rec.put(fieldName, it) }
                        }
                    is StringType -> { rec, p, _ ->
                            p.getString(acc)?.let { rec.put(fieldName, it) }
                        }
                    is DateType -> { rec, p, ch ->
                            p.getDate(acc)?.let {
                                runCatching { LocalDate.parse(it).toEpochDay().toInt() }
                                    .onSuccess { d -> rec.put(fieldName, d) }
                                    .onFailure {
                                        rec.put(fieldName, null)
                                        addError(ch)
                                    }
                            }
                        }
                    is TimeTypeWithTimezone -> { rec, p, ch ->
                            p.getTimeWithTimezone(acc)?.let {
                                runCatching { microsOfDayTz(OffsetTime.parse(it)) }
                                    .onSuccess { t -> rec.put(fieldName, t) }
                                    .onFailure {
                                        rec.put(fieldName, null)
                                        addError(ch)
                                    }
                            }
                        }
                    is TimeTypeWithoutTimezone -> { rec, p, ch ->
                            p.getTimeWithoutTimezone(acc)?.let {
                                runCatching { microsOfDay(LocalTime.parse(it)) }
                                    .onSuccess { t -> rec.put(fieldName, t) }
                                    .onFailure {
                                        rec.put(fieldName, null)
                                        addError(ch)
                                    }
                            }
                        }
                    is TimestampTypeWithTimezone -> { rec, p, ch ->
                            p.getTimestampWithTimezone(acc)?.let {
                                runCatching { epochMicrosTz(OffsetDateTime.parse(it)) }
                                    .onSuccess { t -> rec.put(fieldName, t) }
                                    .onFailure {
                                        rec.put(fieldName, null)
                                        addError(ch)
                                    }
                            }
                        }
                    is TimestampTypeWithoutTimezone -> { rec, p, ch ->
                            p.getTimestampWithoutTimezone(acc)?.let {
                                runCatching { epochMicros(LocalDateTime.parse(it)) }
                                    .onSuccess { t -> rec.put(fieldName, t) }
                                    .onFailure {
                                        rec.put(fieldName, null)
                                        addError(ch)
                                    }
                            }
                        }
                    is UnknownType -> { rec, _, ch ->
                            rec.put(fieldName, null)
                            addError(ch)
                        }
                    else -> { rec, p, ch ->
                            val node = p.getJsonNode(acc)
                            val converted =
                                runCatching {
                                        jsonToParquet(
                                            node,
                                            logicalSchema.properties[acc.name]!!.type,
                                            subSchema,
                                            ch,
                                            acc.name,
                                        )
                                    }
                                    .getOrElse { null }
                            rec.put(fieldName, converted)
                        }
                }

            ColumnWriter(fieldName, acc, subSchema, writer)
        }
    }

    private fun jsonToParquet(
        node: JsonNode?,
        airbyteSchema: AirbyteType,
        avroSchema: Schema,
        ch: MutableList<Meta.Change>,
        path: String
    ): Any? {
        if (node == null || node.isNull) return null

        return try {
            when (airbyteSchema) {
                is ObjectType -> {
                    if (isDisjointUnionSchema(airbyteSchema)) {
                        encodeDisjointUnion(node, airbyteSchema, avroSchema, ch, path)
                    } else {
                        val rec = GenericData.Record(avroSchema)
                        airbyteSchema.properties.forEach { (n, fld) ->
                            val subNode = node.get(n)
                            val subAvro = avroSchema.getField(safe(n)).schema().nonNullOrSelf()
                            rec.put(
                                safe(n),
                                jsonToParquet(subNode, fld.type, subAvro, ch, "$path.$n"),
                            )
                        }
                        rec
                    }
                }
                is ArrayType -> {
                    val arr = GenericData.Array<Any>(node.size(), avroSchema)
                    val elemSchema = avroSchema.elementType.nonNullOrSelf()
                    for (i in 0 until node.size()) {
                        arr.add(
                            jsonToParquet(
                                node.get(i),
                                airbyteSchema.items.type,
                                elemSchema,
                                ch,
                                "$path[$i]"
                            )
                        )
                    }
                    arr
                }

                // unions are already turned into disjoint records in the logical schema
                is UnionType -> {
                    ch.add(
                        Meta.Change(
                            path,
                            AirbyteRecordMessageMetaChange.Change.NULLED,
                            AirbyteRecordMessageMetaChange.Reason.DESTINATION_SERIALIZATION_ERROR,
                        ),
                    )
                    null
                }
                BooleanType -> node.booleanValue()
                IntegerType ->
                    node.bigIntegerValue().let { bi ->
                        if (bi in longMin..longMax) bi.toLong()
                        else
                            null.also {
                                ch.add(
                                    Meta.Change(
                                        path,
                                        AirbyteRecordMessageMetaChange.Change.NULLED,
                                        AirbyteRecordMessageMetaChange.Reason
                                            .DESTINATION_FIELD_SIZE_LIMITATION,
                                    ),
                                )
                            }
                    }
                NumberType -> node.decimalValue().toDouble()
                StringType -> node.textValue()
                DateType -> LocalDate.parse(node.textValue()).toEpochDay().toInt()
                TimeTypeWithTimezone -> microsOfDayTz(OffsetTime.parse(node.textValue()))
                TimeTypeWithoutTimezone -> microsOfDay(LocalTime.parse(node.textValue()))
                TimestampTypeWithTimezone -> epochMicrosTz(OffsetDateTime.parse(node.textValue()))
                TimestampTypeWithoutTimezone -> epochMicros(LocalDateTime.parse(node.textValue()))
                is ObjectTypeWithoutSchema,
                is ObjectTypeWithEmptySchema,
                is ArrayTypeWithoutSchema -> node.toString()
                is UnknownType -> null
            }
        } catch (_: Exception) {
            ch.add(
                Meta.Change(
                    path,
                    AirbyteRecordMessageMetaChange.Change.NULLED,
                    AirbyteRecordMessageMetaChange.Reason.DESTINATION_SERIALIZATION_ERROR,
                ),
            )
            null
        }
    }

    private fun isDisjointUnionSchema(obj: ObjectType): Boolean =
        obj.properties.containsKey("type") && obj.properties.keys.any { it != "type" }

    private fun encodeDisjointUnion(
        node: JsonNode,
        objSchema: ObjectType,
        avro: Schema,
        ch: MutableList<Meta.Change>,
        path: String
    ): GenericRecord? {
        val rec = GenericData.Record(avro)

        val candidates: List<Pair<String, FieldType>> =
            objSchema.properties.entries.filter { it.key != "type" }.map { it.key to it.value }

        val chosen: Pair<String, FieldType>? =
            candidates.firstOrNull { (_, field) -> nodeMatches(node, field.type) }

        if (chosen == null) {
            ch.add(
                Meta.Change(
                    path,
                    AirbyteRecordMessageMetaChange.Change.NULLED,
                    AirbyteRecordMessageMetaChange.Reason.DESTINATION_SERIALIZATION_ERROR,
                ),
            )
            return null
        }

        val (optName, optField) = chosen
        val optAvro = avro.getField(safe(optName)).schema().nonNullOrSelf()

        rec.put("type", optName)
        rec.put(safe(optName), jsonToParquet(node, optField.type, optAvro, ch, "$path.$optName"))

        return rec
    }

    private fun nodeMatches(node: JsonNode, schema: AirbyteType): Boolean =
        when (schema) {
            is StringType -> node.isTextual
            is BooleanType -> node.isBoolean
            is IntegerType -> node.isIntegralNumber
            is NumberType -> node.isNumber
            is DateType,
            is TimeTypeWithTimezone,
            is TimeTypeWithoutTimezone,
            is TimestampTypeWithTimezone,
            is TimestampTypeWithoutTimezone -> node.isTextual
            is ObjectType,
            is ObjectTypeWithoutSchema,
            is ObjectTypeWithEmptySchema -> node.isObject
            is ArrayType,
            is ArrayTypeWithoutSchema -> node.isArray
            is UnionType -> schema.options.any { nodeMatches(node, it) }
            is UnknownType -> false
        }

    private fun buildMeta(syncId: Long, changes: List<Meta.Change>): GenericRecord {
        val meta = GenericData.Record(metaSchema)
        meta.put("sync_id", syncId)

        val array = GenericData.Array<GenericRecord>(changes.size, changeArraySchema)
        changes.forEach { c ->
            val rec = GenericData.Record(changeRecordSchema)
            rec.put("field", c.field)
            rec.put("change", c.change.name)
            rec.put("reason", c.reason.name)
            array.add(rec)
        }
        meta.put("changes", array)
        return meta
    }

    private fun mergeUnions(schema: AirbyteType): AirbyteType =
        when (schema) {
            is UnionType -> mergeUnion(schema)
            is ObjectType ->
                ObjectType(
                    schema.properties
                        .mapValues { (_, f) -> f.copy(type = mergeUnions(f.type)) }
                        .toMutableMap() as LinkedHashMap<String, FieldType>,
                )
            is ArrayType ->
                ArrayType(
                    FieldType(
                        mergeUnions(schema.items.type),
                        schema.items.nullable,
                    ),
                )
            else -> schema
        }

    private fun mergeUnion(schema: AirbyteType): AirbyteType =
        if (schema is UnionType) {
            val mapped = schema.options.map { mergeUnions(it) }
            val merged = mutableSetOf<AirbyteType>()
            foldUnionOptions(merged, mapped)
            UnionType.of(merged)
        } else schema

    private fun foldUnionOptions(into: MutableSet<AirbyteType>, from: Iterable<AirbyteType>) {
        for (opt in from) when (opt) {
            is UnionType -> foldUnionOptions(into, opt.options)
            is ObjectType -> mergeObjectOption(into, opt)
            else -> into += opt
        }
    }

    private fun mergeObjectOption(into: MutableSet<AirbyteType>, opt: ObjectType) {
        val existing = into.find { it is ObjectType } as ObjectType?
        if (existing == null) {
            into += opt
            return
        }
        into -= existing
        val props = LinkedHashMap(existing.properties)
        opt.properties.forEach { (name, field) ->
            val prev = props[name]
            props[name] =
                if (prev == null) field
                else
                    FieldType(
                        mergeUnion(UnionType.of(prev.type, field.type)),
                        prev.nullable || field.nullable,
                    )
        }
        into += ObjectType(props)
    }

    private fun unionToDisjointRecord(schema: AirbyteType): AirbyteType =
        when (schema) {
            is UnionType -> toDisjoint(schema)
            is ObjectType ->
                ObjectType(
                    schema.properties
                        .mapValues { (_, f) -> f.copy(type = unionToDisjointRecord(f.type)) }
                        .toMutableMap() as LinkedHashMap<String, FieldType>,
                )
            is ArrayType ->
                ArrayType(
                    FieldType(unionToDisjointRecord(schema.items.type), schema.items.nullable)
                )
            else -> schema
        }

    private fun toDisjoint(schema: UnionType): AirbyteType {
        if (schema.options.size < 2) return unionToDisjointRecord(schema.options.first())
        val props = linkedMapOf<String, FieldType>()
        props["type"] = FieldType(StringType, false)
        schema.options.forEach { opt ->
            val mapped = unionToDisjointRecord(opt)
            val name = typeName(mapped)
            if (props.containsKey(name)) {
                throw IllegalArgumentException("Union of types with same name: $name")
            }
            props[name] = FieldType(mapped, true)
        }
        return ObjectType(props)
    }

    private fun typeName(type: AirbyteType): String =
        when (type) {
            is StringType -> "string"
            is BooleanType -> "boolean"
            is IntegerType -> "integer"
            is NumberType -> "number"
            is DateType -> "date"
            is TimestampTypeWithTimezone -> "timestamp_with_timezone"
            is TimestampTypeWithoutTimezone -> "timestamp_without_timezone"
            is TimeTypeWithTimezone -> "time_with_timezone"
            is TimeTypeWithoutTimezone -> "time_without_timezone"
            is ArrayType -> "array"
            is ObjectType -> "object"
            is ArrayTypeWithoutSchema,
            is ObjectTypeWithoutSchema,
            is ObjectTypeWithEmptySchema -> "object"
            is UnionType -> "union"
            is UnknownType -> "unknown"
        }

    private fun microsOfDayTz(ot: OffsetTime): Long =
        ot.withOffsetSameInstant(ZoneOffset.UTC).toLocalTime().toNanoOfDay() / 1_000

    private fun microsOfDay(t: LocalTime): Long = t.toNanoOfDay() / 1_000

    private fun epochMicrosTz(odt: OffsetDateTime): Long {
        val inst = odt.toInstant().truncatedTo(ChronoUnit.MICROS)
        return inst.epochSecond * 1_000_000 + inst.nano / 1_000
    }

    private fun epochMicros(dt: LocalDateTime): Long =
        dt.toInstant(ZoneOffset.UTC).let { it.epochSecond * 1_000_000 + it.nano / 1_000 }

    private fun Schema.nonNullOrSelf(): Schema =
        if (
            type == Schema.Type.UNION &&
                types.size == 2 &&
                types.any { it.type == Schema.Type.NULL }
        )
            types.first { it.type != Schema.Type.NULL }
        else this

    private fun Schema.nonNullSubSchemaOf(field: String): Schema =
        getField(field)?.schema()?.nonNullOrSelf() ?: error("Field '$field' not found in schema.")
}
