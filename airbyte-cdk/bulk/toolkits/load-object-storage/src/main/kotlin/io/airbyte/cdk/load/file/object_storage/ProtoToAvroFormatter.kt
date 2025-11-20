/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.load.file.object_storage

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.command.object_storage.AvroFormatConfiguration
import io.airbyte.cdk.load.data.AirbyteType
import io.airbyte.cdk.load.data.AirbyteValueProxy
import io.airbyte.cdk.load.data.ArrayType
import io.airbyte.cdk.load.data.ArrayTypeWithoutSchema
import io.airbyte.cdk.load.data.BooleanType
import io.airbyte.cdk.load.data.DateType
import io.airbyte.cdk.load.data.FieldType
import io.airbyte.cdk.load.data.IntegerType
import io.airbyte.cdk.load.data.NumberType
import io.airbyte.cdk.load.data.ObjectType
import io.airbyte.cdk.load.data.ObjectTypeWithEmptySchema
import io.airbyte.cdk.load.data.ObjectTypeWithoutSchema
import io.airbyte.cdk.load.data.StringType
import io.airbyte.cdk.load.data.TimeTypeWithTimezone
import io.airbyte.cdk.load.data.TimeTypeWithoutTimezone
import io.airbyte.cdk.load.data.TimestampTypeWithTimezone
import io.airbyte.cdk.load.data.TimestampTypeWithoutTimezone
import io.airbyte.cdk.load.data.Transformations
import io.airbyte.cdk.load.data.UnionType
import io.airbyte.cdk.load.data.UnknownType
import io.airbyte.cdk.load.data.avro.toAvroSchema
import io.airbyte.cdk.load.data.collectUnknownPaths
import io.airbyte.cdk.load.data.withAirbyteMeta
import io.airbyte.cdk.load.file.avro.toAvroWriter
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

class ProtoToAvroFormatter(
    private val stream: DestinationStream,
    outputStream: OutputStream,
    formatConfig: AvroFormatConfiguration,
    private val rootLevelFlattening: Boolean,
) : ObjectStorageFormattingWriter {
    private val longMin = Long.MIN_VALUE.toBigInteger()
    private val longMax = Long.MAX_VALUE.toBigInteger()

    private val logicalSchema: ObjectType =
        mergeUnions(stream.schema).withAirbyteMeta(rootLevelFlattening)
    private val avroSchema: Schema = logicalSchema.toAvroSchema(stream.mappedDescriptor)
    private val writer =
        outputStream.toAvroWriter(avroSchema, formatConfig.avroCompressionConfiguration)

    private fun safe(name: String) = Transformations.toAvroSafeName(name)

    // meta
    private val metaSchema = avroSchema.nonNullSubSchemaOf(safe(Meta.COLUMN_NAME_AB_META))
    private val changeArraySchema = metaSchema.getField("changes").schema().nonNullOrSelf()
    private val changeRecordSchema = changeArraySchema.elementType.nonNullOrSelf()

    // column table
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
            throw RuntimeException("Avro format doesn't support non-flattening mode")
        }
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
                        mergeUnion(UnionType.of(prev.type, field.type)), // ← no cast needed
                        prev.nullable || field.nullable,
                    )
        }
        into += ObjectType(props)
    }

    override fun accept(record: DestinationRecordRaw) {
        val src =
            record.rawData as? DestinationRecordProtobufSource
                ?: error("expects DestinationRecordProtobufSource")

        val proxy = src.asAirbyteValueProxy()
        val errors = mutableListOf<Meta.Change>()

        val root = GenericData.Record(avroSchema)

        // meta fields
        root.put(Meta.COLUMN_NAME_AB_RAW_ID, record.airbyteRawId.toString())
        root.put(Meta.COLUMN_NAME_AB_EXTRACTED_AT, src.emittedAtMs)
        root.put(Meta.COLUMN_NAME_AB_GENERATION_ID, record.stream.generationId)

        // payload
        if (rootLevelFlattening) {
            colWriters.forEach { it.write(root, proxy, errors) }
        } else {
            throw RuntimeException("Avro format doesn't support non-flattening mode")
        }

        // _airbyte_meta
        root.put(
            Meta.COLUMN_NAME_AB_META,
            buildMeta(record.stream.syncId, src.sourceMeta.changes + errors),
        )

        writer.write(root)
    }

    override fun flush() = writer.flush()
    override fun close() = writer.close()
    private fun buildColumnWriters(): List<ColumnWriter> {
        val accessors = stream.airbyteValueProxyFieldAccessors

        return accessors.map { acc ->
            val (subSchema, fieldName) =
                if (rootLevelFlattening) {
                    val n = safe(acc.name)
                    avroSchema.getField(n).schema().nonNullOrSelf() to n
                } else {
                    throw RuntimeException("Avro format doesn't support non-flattening mode")
                }

            fun addError(ch: MutableList<Meta.Change>) =
                ch.add(
                    Meta.Change(
                        if (rootLevelFlattening) acc.name
                        else
                            throw RuntimeException(
                                "Avro format doesn't support non-flattening mode"
                            ),
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
                                            pathFor(acc.name),
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
                                        jsonToAvro(
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

    private fun jsonToAvro(
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
                    val rec = GenericData.Record(avroSchema)
                    airbyteSchema.properties.forEach { (n, fld) ->
                        val subNode = node.get(n)
                        val subAvro = avroSchema.getField(safe(n)).schema().nonNullOrSelf()
                        rec.put(
                            safe(n),
                            jsonToAvro(subNode, fld.type, subAvro, ch, "$path.$n"),
                        )
                    }
                    rec
                }
                is ArrayType -> {
                    val arr = GenericData.Array<Any>(node.size(), avroSchema)
                    val elemSchema = avroSchema.elementType.nonNullOrSelf()
                    for (i in 0 until node.size()) {
                        arr.add(
                            jsonToAvro(
                                node.get(i),
                                airbyteSchema.items.type,
                                elemSchema,
                                ch,
                                "$path[$i]",
                            ),
                        )
                    }
                    arr
                }
                is UnionType -> {
                    // Choose the first option compatible with BOTH the JsonNode and the Avro union
                    // branches
                    val (chosenOpt, avroBranch) =
                        pickUnionBranch(node, airbyteSchema, avroSchema)
                            ?: run {
                                ch.add(
                                    Meta.Change(
                                        path,
                                        AirbyteRecordMessageMetaChange.Change.NULLED,
                                        AirbyteRecordMessageMetaChange.Reason
                                            .DESTINATION_SERIALIZATION_ERROR,
                                    ),
                                )
                                return null
                            }

                    jsonToAvro(node, chosenOpt, avroBranch, ch, path)
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

    private fun pickUnionBranch(
        node: JsonNode,
        airbyteUnion: UnionType,
        avroUnion: Schema
    ): Pair<AirbyteType, Schema>? {
        for (opt in airbyteUnion.options) {
            if (!nodeMatches(node, opt)) continue // wrong json kind
            val branch = matchingAvroType(opt, avroUnion) ?: continue
            return opt to branch
        }
        return null
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

    private fun matchingAvroType(airbyteSchema: AirbyteType, avroUnion: Schema): Schema? =
        when (airbyteSchema) {
            is ObjectType -> avroUnion.types.find { it.type == Schema.Type.RECORD }
            is ArrayType -> avroUnion.types.find { it.type == Schema.Type.ARRAY }
            BooleanType -> avroUnion.types.find { it.type == Schema.Type.BOOLEAN }
            DateType -> avroUnion.types.find { it.type == Schema.Type.INT }
            IntegerType -> avroUnion.types.find { it.type == Schema.Type.LONG }
            NumberType -> avroUnion.types.find { it.type == Schema.Type.DOUBLE }
            StringType,
            is ObjectTypeWithEmptySchema,
            is ObjectTypeWithoutSchema,
            is ArrayTypeWithoutSchema,
            is UnknownType -> avroUnion.types.find { it.type == Schema.Type.STRING }
            TimeTypeWithTimezone,
            TimeTypeWithoutTimezone,
            TimestampTypeWithTimezone,
            TimestampTypeWithoutTimezone -> avroUnion.types.find { it.type == Schema.Type.LONG }
            is UnionType -> null
        }

    private fun pathFor(n: String) =
        if (rootLevelFlattening) n
        else throw RuntimeException("Avro format doesn't support non-flattening mode")

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
