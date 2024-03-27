package io.airbyte.cdk.components.cursor

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ArrayNode
import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.components.ConsumerComponent
import io.airbyte.commons.jackson.MoreMappers
import io.airbyte.commons.json.Jsons
import io.airbyte.protocol.models.JsonSchemaType
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream
import java.math.BigDecimal
import java.math.BigInteger
import java.nio.ByteBuffer
import java.util.*
import java.util.concurrent.atomic.AtomicLong
import kotlin.collections.ArrayList

class CursorConsumer
private constructor(
    val leafMappers: Map<ColumnSchema.LeafType, (Any?) -> JsonNode>,
    val arrayMapper: (Any?) -> Iterable<Any?>,
    val columns: List<Pair<String, ColumnSchema>>,
    @JvmField val maxRecords: Long,
    @JvmField val maxRecordBytes: Long,
) : ConsumerComponent<List<Any?>, ObjectNode> {

    private val numRecords = AtomicLong()
    private val numRecordBytes = AtomicLong()
    private val buffer: MutableList<JsonNode> = Collections.synchronizedList(ArrayList(1_000_000))

    private val mappers: List<(Any?) -> JsonNode> =
        columns.map { (name, schema) -> buildMapper(name, schema) }

    private fun buildMapper(columnName: String, schema: ColumnSchema): (Any?) -> JsonNode {
        val type = schema.asColumnType()
        val mapperInner = buildMapperRecursive(type)
        return { v: Any? ->
            try {
                mapperInner(v)
            } catch (e: Exception) {
                throw RuntimeException("$columnName value $v not suitable for $type", e)
            }
        }
    }

    private fun buildMapperRecursive(type: ColumnSchema.ColumnType): (Any?) -> JsonNode = when(type) {
        is ColumnSchema.LeafType -> leafMappers[type] ?: throw IllegalArgumentException("missing mapper for $type")
        is ColumnSchema.ArrayColumnType -> { v: Any? ->
            Jsons.arrayNode().apply { addAll(arrayMapper(v).map(buildMapperRecursive(type.item)).toList()) }
        }
    }

    override fun shouldCheckpoint(): Boolean =
        numRecords.get() >= maxRecords || numRecordBytes.get() >= maxRecordBytes

    override fun flush(): Sequence<ObjectNode> =
        buffer.asSequence().chunked(columns.size).map { values: List<JsonNode> ->
            val objectNode: ObjectNode = Jsons.emptyObject() as ObjectNode
            columns.forEachIndexed { i, (columnName, _) -> objectNode.set<JsonNode>(columnName, values[i]) }
            objectNode
        }

    override fun accept(row: List<Any?>) {
        val values = row.mapIndexed { i, v -> mappers[i](v) }
        buffer.addAll(values)
        numRecords.getAndIncrement()
        numRecordBytes.getAndAdd(values.sumOf { it.toString().length.toLong() })
    }

    class Builder(
        @JvmField val maxRecords: Long = Long.MAX_VALUE,
        @JvmField val maxRecordBytes: Long = Long.MAX_VALUE,
    ) : ConsumerComponent.Builder<List<Any?>, ObjectNode> {

        private lateinit var columns: List<Pair<String, ColumnSchema>>

        val valueMappers = ColumnSchema.LeafType.entries.map { Pair(it, it.mapper) }.toMap().toMutableMap()
        var arrayMapper: (Any?) -> Iterable<Any?> = ColumnSchema.ArrayColumnType.arrayMapper

        inline fun <reified T> withArrayMapping(crossinline mapping : (T) -> Iterable<Any?>): Builder = apply {
            val nextArrayMapper = arrayMapper
            arrayMapper = { value: Any? ->
                when (value) {
                    is T -> mapping(value)
                    else -> nextArrayMapper(value)
                }
            }
        }

        inline fun <reified T> withMapping(type: ColumnSchema.LeafType, crossinline mapping : (T) -> JsonNode): Builder = apply {
            val nextMapper = valueMappers[type]!!
            valueMappers[type] = { value: Any? ->
                when (value) {
                    is T -> mapping(value)
                    else -> nextMapper(value)
                }
            }
        }

        fun withAirbyteStream(configuredAirbyteStream: ConfiguredAirbyteStream): Builder = apply {
            val jsonSchema = configuredAirbyteStream.stream.jsonSchema["properties"] as ObjectNode
            columns = jsonSchema.fieldNames().asSequence().toList().sorted().map { c ->
                Pair(c, ColumnSchema(jsonSchema[c]))
            }
        }

        override fun build(): ConsumerComponent<List<Any?>, ObjectNode> =
            CursorConsumer(EnumMap(valueMappers), arrayMapper, columns, maxRecords, maxRecordBytes)
    }
}
