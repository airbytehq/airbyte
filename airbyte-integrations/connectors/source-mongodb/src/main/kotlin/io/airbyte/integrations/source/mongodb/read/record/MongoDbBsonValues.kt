/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.mongodb.read.record

import com.fasterxml.jackson.core.JsonGenerator
import io.airbyte.cdk.util.Jsons
import java.io.Writer
import java.math.BigDecimal
import java.time.Instant
import java.time.ZoneOffset
import java.time.format.DateTimeFormatter
import java.time.format.DateTimeFormatterBuilder
import java.time.format.SignStyle
import java.time.temporal.ChronoField
import java.util.Base64
import org.bson.BsonDocument
import org.bson.BsonDocumentReader
import org.bson.BsonReader
import org.bson.BsonRegularExpression
import org.bson.BsonTimestamp
import org.bson.BsonType
import org.bson.BsonValue
import org.bson.types.Decimal128

/**
 * Reads BSON as the connector emits it, in one pass and without decoding to objects: `ObjectId` as
 * hex, `Date` with milliseconds, binaries of any subtype as Base64, regex as `(options)pattern`,
 * `CodeWithScope` as an object, `Decimal128` exact, a non-finite number as its name in text.
 * `MinKey`, `MaxKey`, `undefined` and `DBPointer` are dropped: null as a field, omitted inside a
 * document, `null` inside an array. Not thread-safe: the JSON text is written through one reused
 * generator.
 */
class MongoDbBsonValues {

    private val buffer = StringBuilder()
    private val generator: JsonGenerator =
        Jsons.createGenerator(
                object : Writer() {
                    override fun write(cbuf: CharArray, off: Int, len: Int) {
                        buffer.append(cbuf, off, len)
                    }

                    override fun flush() {}

                    override fun close() {}
                },
            )
            .setRootValueSeparator(null)

    /** The value the [reader] is positioned at, or null when its kind is dropped. */
    fun readValue(reader: BsonReader, type: BsonType): MongoDbValue? =
        when (type) {
            BsonType.DOUBLE -> number(reader.readDouble())
            BsonType.STRING -> MongoDbValue.Text(reader.readString())
            BsonType.DOCUMENT -> MongoDbValue.Json(documentText(reader), isArray = false)
            BsonType.ARRAY -> MongoDbValue.Json(arrayText(reader), isArray = true)
            BsonType.BINARY -> MongoDbValue.Text(base64(reader.readBinaryData().data))
            BsonType.OBJECT_ID -> MongoDbValue.Text(reader.readObjectId().toHexString())
            BsonType.BOOLEAN -> MongoDbValue.Bool(reader.readBoolean())
            BsonType.DATE_TIME -> MongoDbValue.Text(formatDate(reader.readDateTime()))
            BsonType.NULL -> {
                reader.readNull()
                MongoDbValue.Null
            }
            BsonType.REGULAR_EXPRESSION ->
                MongoDbValue.Text(regexText(reader.readRegularExpression()))
            BsonType.JAVASCRIPT -> MongoDbValue.Text(reader.readJavaScript())
            BsonType.SYMBOL -> MongoDbValue.Text(reader.readSymbol())
            BsonType.JAVASCRIPT_WITH_SCOPE ->
                MongoDbValue.Json(text { writeCodeWithScope(reader, it) }, isArray = false)
            BsonType.INT32 -> MongoDbValue.Num(reader.readInt32())
            BsonType.TIMESTAMP -> MongoDbValue.Text(formatTimestamp(reader.readTimestamp()))
            BsonType.INT64 -> MongoDbValue.Num(reader.readInt64())
            BsonType.DECIMAL128 -> number(reader.readDecimal128())
            BsonType.UNDEFINED,
            BsonType.DB_POINTER,
            BsonType.MIN_KEY,
            BsonType.MAX_KEY -> {
                reader.skipValue()
                null
            }
            BsonType.END_OF_DOCUMENT -> error("no value to read")
        }

    /** [readValue] of an already decoded value. */
    fun valueOf(value: BsonValue): MongoDbValue? {
        val reader = BsonDocumentReader(BsonDocument(WRAPPER_FIELD, value))
        reader.readStartDocument()
        val type: BsonType = reader.readBsonType()
        reader.readName()
        return readValue(reader, type)
    }

    /** The compact JSON of the document the [reader] is positioned at. */
    fun documentText(reader: BsonReader): String = text { writeDocument(reader, it) }

    private fun arrayText(reader: BsonReader): String = text { writeArray(reader, it) }

    private inline fun text(write: (JsonGenerator) -> Unit): String {
        write(generator)
        generator.flush()
        val text = buffer.toString()
        buffer.setLength(0)
        return text
    }

    private fun writeDocument(reader: BsonReader, gen: JsonGenerator) {
        reader.readStartDocument()
        gen.writeStartObject()
        while (true) {
            val type: BsonType = reader.readBsonType()
            if (type == BsonType.END_OF_DOCUMENT) break
            val name: String = reader.readName()
            if (isDropped(type)) {
                reader.skipValue()
                continue
            }
            gen.writeFieldName(name)
            writeValue(reader, gen, type)
        }
        reader.readEndDocument()
        gen.writeEndObject()
    }

    private fun writeArray(reader: BsonReader, gen: JsonGenerator) {
        reader.readStartArray()
        gen.writeStartArray()
        while (true) {
            val type: BsonType = reader.readBsonType()
            if (type == BsonType.END_OF_DOCUMENT) break
            if (isDropped(type)) {
                reader.skipValue()
                gen.writeNull()
                continue
            }
            writeValue(reader, gen, type)
        }
        reader.readEndArray()
        gen.writeEndArray()
    }

    private fun writeCodeWithScope(reader: BsonReader, gen: JsonGenerator) {
        gen.writeStartObject()
        gen.writeStringField(CODE_FIELD, reader.readJavaScriptWithScope())
        gen.writeFieldName(SCOPE_FIELD)
        writeDocument(reader, gen)
        gen.writeEndObject()
    }

    private fun writeValue(reader: BsonReader, gen: JsonGenerator, type: BsonType) {
        when (type) {
            BsonType.DOUBLE -> writeNumber(gen, reader.readDouble())
            BsonType.STRING -> gen.writeString(reader.readString())
            BsonType.DOCUMENT -> writeDocument(reader, gen)
            BsonType.ARRAY -> writeArray(reader, gen)
            BsonType.BINARY -> gen.writeString(base64(reader.readBinaryData().data))
            BsonType.OBJECT_ID -> gen.writeString(reader.readObjectId().toHexString())
            BsonType.BOOLEAN -> gen.writeBoolean(reader.readBoolean())
            BsonType.DATE_TIME -> gen.writeString(formatDate(reader.readDateTime()))
            BsonType.NULL -> {
                reader.readNull()
                gen.writeNull()
            }
            BsonType.REGULAR_EXPRESSION ->
                gen.writeString(regexText(reader.readRegularExpression()))
            BsonType.JAVASCRIPT -> gen.writeString(reader.readJavaScript())
            BsonType.SYMBOL -> gen.writeString(reader.readSymbol())
            BsonType.JAVASCRIPT_WITH_SCOPE -> writeCodeWithScope(reader, gen)
            BsonType.INT32 -> gen.writeNumber(reader.readInt32())
            BsonType.TIMESTAMP -> gen.writeString(formatTimestamp(reader.readTimestamp()))
            BsonType.INT64 -> gen.writeNumber(reader.readInt64())
            BsonType.DECIMAL128 -> writeNumber(gen, reader.readDecimal128())
            BsonType.UNDEFINED,
            BsonType.DB_POINTER,
            BsonType.MIN_KEY,
            BsonType.MAX_KEY,
            BsonType.END_OF_DOCUMENT -> error("dropped kinds are skipped before writing")
        }
    }

    private fun isDropped(type: BsonType): Boolean =
        type == BsonType.UNDEFINED ||
            type == BsonType.DB_POINTER ||
            type == BsonType.MIN_KEY ||
            type == BsonType.MAX_KEY

    private fun number(value: Double): MongoDbValue =
        if (value.isFinite()) MongoDbValue.Num(value) else MongoDbValue.Text(value.toString())

    private fun number(value: Decimal128): MongoDbValue =
        finite(value)?.let(MongoDbValue::Num) ?: MongoDbValue.Text(value.toString())

    private fun writeNumber(gen: JsonGenerator, value: Double) {
        if (value.isFinite()) gen.writeNumber(value) else gen.writeString(value.toString())
    }

    private fun writeNumber(gen: JsonGenerator, value: Decimal128) {
        when (val number: Number? = finite(value)) {
            null -> gen.writeString(value.toString())
            is BigDecimal -> gen.writeNumber(number)
            else -> gen.writeNumber(number.toDouble())
        }
    }

    /**
     * Exact, or null for NaN and the infinities; a negative zero, which no [BigDecimal] can carry,
     * is the double `-0.0`.
     */
    private fun finite(value: Decimal128): Number? =
        when {
            value.isNaN || value.isInfinite -> null
            else ->
                try {
                    value.bigDecimalValue()
                } catch (_: ArithmeticException) {
                    -0.0
                }
        }

    private fun base64(bytes: ByteArray): String = Base64.getEncoder().encodeToString(bytes)

    /** `(options)pattern`, or just the pattern when there are no options. */
    private fun regexText(regex: BsonRegularExpression): String =
        if (regex.options.isNullOrBlank()) regex.pattern else "(${regex.options})${regex.pattern}"

    private fun formatDate(epochMillis: Long): String =
        ISO_MILLIS.format(Instant.ofEpochMilli(epochMillis))

    /** The raw 64-bit `BsonTimestamp` value formatted as if it were epoch millis. */
    private fun formatTimestamp(timestamp: BsonTimestamp): String =
        ISO_MILLIS.format(Instant.ofEpochMilli(timestamp.value))

    private companion object {
        const val WRAPPER_FIELD = "v"
        const val CODE_FIELD = "code"
        const val SCOPE_FIELD = "scope"

        /**
         * `yyyy-MM-dd'T'HH:mm:ss.SSS'Z'` in UTC: milliseconds always present, no sign on a year
         * beyond 9999 (unlike `Instant.toString()`).
         */
        val ISO_MILLIS: DateTimeFormatter =
            DateTimeFormatterBuilder()
                .appendValue(ChronoField.YEAR, 4, 10, SignStyle.NORMAL)
                .appendPattern("-MM-dd'T'HH:mm:ss.SSS'Z'")
                .toFormatter()
                .withZone(ZoneOffset.UTC)
    }
}
