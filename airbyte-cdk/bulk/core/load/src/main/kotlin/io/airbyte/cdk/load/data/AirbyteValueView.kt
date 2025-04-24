package io.airbyte.cdk.load.data

import com.fasterxml.jackson.databind.node.ObjectNode
import com.google.flatbuffers.ByteVector
import com.google.flatbuffers.UnionVector
import io.airbyte.protocol.AirbyteBooleanValue
import io.airbyte.protocol.AirbyteLongValue
import io.airbyte.protocol.AirbyteNumberValue
import io.airbyte.protocol.AirbyteRecord
import io.airbyte.protocol.AirbyteStringValue
import java.security.MessageDigest
import java.time.LocalDateTime
import java.time.ZoneOffset
import java.util.HexFormat

enum class AirbyteValueViewType {
    STRING,
    BOOLEAN,
    INTEGER,
    NUMBER,
    BINARY,
    TIMESTAMP
}

private val fakeSortedCatalogLocal: List<Pair<String, AirbyteValueViewType>> =
    listOf(
        Pair("occupation", AirbyteValueViewType.STRING),
        Pair("gender", AirbyteValueViewType.STRING),
        Pair("global_id", AirbyteValueViewType.INTEGER),
        Pair("academic_degree", AirbyteValueViewType.STRING),
        Pair("weight", AirbyteValueViewType.INTEGER),
        Pair("created_at", AirbyteValueViewType.TIMESTAMP),
        Pair("language", AirbyteValueViewType.STRING),
        Pair("telephone", AirbyteValueViewType.STRING),
        Pair("title", AirbyteValueViewType.STRING),
        Pair("updated_at", AirbyteValueViewType.TIMESTAMP),
        Pair("nationality", AirbyteValueViewType.STRING),
        Pair("blood_type", AirbyteValueViewType.STRING),
        Pair("name", AirbyteValueViewType.STRING),
        Pair("id", AirbyteValueViewType.INTEGER),
        Pair("age", AirbyteValueViewType.INTEGER),
        Pair("email", AirbyteValueViewType.STRING),
        Pair("height", AirbyteValueViewType.NUMBER),
    )

private val fakeSortedCatalogCloud: List<Pair<String, AirbyteValueViewType>> =
    listOf(
        Pair("id", AirbyteValueViewType.INTEGER),
        Pair("age", AirbyteValueViewType.INTEGER),
        Pair("name", AirbyteValueViewType.STRING),
        Pair("email", AirbyteValueViewType.STRING),
        Pair("title", AirbyteValueViewType.STRING),
        Pair("gender", AirbyteValueViewType.STRING),
        Pair("height", AirbyteValueViewType.NUMBER),
        Pair("weight", AirbyteValueViewType.INTEGER),
        Pair("language", AirbyteValueViewType.STRING),
        Pair("global_id", AirbyteValueViewType.INTEGER),
        Pair("telephone", AirbyteValueViewType.STRING),
        Pair("blood_type", AirbyteValueViewType.STRING),
        Pair("created_at", AirbyteValueViewType.TIMESTAMP),
        Pair("occupation", AirbyteValueViewType.STRING),
        Pair("updated_at", AirbyteValueViewType.TIMESTAMP),
        Pair("nationality", AirbyteValueViewType.STRING),
        Pair("academic_degree", AirbyteValueViewType.STRING),
    )

interface AirbyteValueView {
    val finalSchema: List<Pair<String, AirbyteValueViewType>>
        get() = fakeSortedCatalogCloud

    fun getString(idx: Int): String?
    fun getBoolean(idx: Int): Boolean?
    fun getInteger(idx: Int): Long?
    fun getNumber(idx: Int): Double?
    fun getTimestamp(idx: Int): LocalDateTime?
}

class AirbyteValueProtoView(
    private val underlying: List<AirbyteRecord.AirbyteValue>
): AirbyteValueView {
    override fun getString(idx: Int): String {
        return underlying[idx].string
    }

    override fun getBoolean(idx: Int): Boolean {
        return underlying[idx].boolean
    }

    override fun getInteger(idx: Int): Long {
        return underlying[idx].integer
    }

    override fun getNumber(idx: Int): Double {
        return underlying[idx].number
    }

    override fun getTimestamp(idx: Int): LocalDateTime {
        val ts = underlying[idx].timestamp
        return LocalDateTime.ofEpochSecond(
            ts.seconds,
            ts.nanos,
            ZoneOffset.UTC
        )
    }
}

class AirbyteValueFlatbufferView(
    private val typeVector: ByteVector,
    private val underlying: UnionVector,
) : AirbyteValueView {
    private val boolObject = AirbyteBooleanValue()
    private val stringObject = AirbyteStringValue()
    private val integerObject = AirbyteLongValue()
    private val numberObject = AirbyteNumberValue()

    override fun getString(idx: Int): String? {
        if (typeVector.get(idx) == 0.toByte()) {
            return null
        }
        underlying.get(stringObject, idx)
        return stringObject.value()
    }

    override fun getBoolean(idx: Int): Boolean? {
        if (typeVector.get(idx) == 0.toByte()) {
            return null
        }
        underlying.get(boolObject, idx)
        return boolObject.value()
    }

    override fun getInteger(idx: Int): Long? {
        if (typeVector.get(idx) == 0.toByte()) {
            return null
        }
        underlying.get(integerObject, idx)
        return integerObject.value()
    }

    override fun getNumber(idx: Int): Double? {
        if (typeVector.get(idx) == 0.toByte()) {
            return 0.0
        }
        underlying.get(numberObject, idx)
        return numberObject.value()
    }

    override fun getTimestamp(idx: Int): LocalDateTime? {
        if (typeVector.get(idx) == 0.toByte()) {
            return null
        }
        underlying.get(integerObject, idx)
        val millis = integerObject.value()
        return LocalDateTime.ofEpochSecond(
            millis / 1000,
            (millis % 1000).toInt() * 1_000_000,
            ZoneOffset.UTC
        )
    }

    override fun toString(): String {
        return underlying.toString()
    }
}

class AirbyteValueJsonNodeView(
    private val underlying: ObjectNode,
): AirbyteValueView {
    private val indexToName: Map<Int, String> =
        fakeSortedCatalogLocal.mapIndexed { index, pair -> index to pair.first }.toMap()

    override fun getString(idx: Int): String {
        return underlying.get(indexToName[idx]!!).asText()
    }

    override fun getBoolean(idx: Int): Boolean {
        return underlying.get(indexToName[idx]!!).asBoolean()
    }

    override fun getInteger(idx: Int): Long {
        return underlying.get(indexToName[idx]!!).asLong()
    }

    override fun getNumber(idx: Int): Double {
        return underlying.get(indexToName[idx]!!).asDouble()
    }

    override fun getTimestamp(idx: Int): LocalDateTime {
        return LocalDateTime.parse(underlying.get(indexToName[idx]!!).asText())
    }
}

interface AirbyteValueViewMapper {
    // TODO: Map schema intelligently
    fun wrap(underlying: AirbyteValueView): AirbyteValueView
}

abstract class AirbyteValueIdentityView(
    val underlying: AirbyteValueView
): AirbyteValueView {
    override fun getString(idx: Int): String? {
        return underlying.getString(idx)
    }

    override fun getBoolean(idx: Int): Boolean? {
        return underlying.getBoolean(idx)
    }

    override fun getInteger(idx: Int): Long? {
        return underlying.getInteger(idx)
    }

    override fun getNumber(idx: Int): Double? {
        return underlying.getNumber(idx)
    }

    override fun getTimestamp(idx: Int): LocalDateTime? {
        return underlying.getTimestamp(idx)
    }
}

class AirbyteValueHashingView(
    underlying: AirbyteValueView,
    private val indexesToHash: Set<Int>,
): AirbyteValueIdentityView(underlying) {
    override fun getString(idx: Int): String? {
        return if (indexesToHash.contains(idx)) {
            underlying.getString(idx)?.toByteArray()?.let {
                HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(it))
            }
        } else {
            underlying.getString(idx)
        }
    }
}

class AirbyteValueHashViewMapper(
    private val indexesToHash: Set<Int>,
): AirbyteValueViewMapper {
    override fun wrap(underlying: AirbyteValueView): AirbyteValueView {
        return AirbyteValueHashingView(underlying, indexesToHash)
    }
}


