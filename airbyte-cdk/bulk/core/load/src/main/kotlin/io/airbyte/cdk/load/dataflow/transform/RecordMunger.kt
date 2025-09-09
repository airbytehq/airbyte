package io.airbyte.cdk.load.dataflow.transform

import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.message.DestinationRecordProtobufSource
import io.airbyte.cdk.load.message.DestinationRecordRaw
import jakarta.inject.Singleton

/*
 * Munges values and keys into a simple map form. Encapsulates
 * EnrichedAirbyteValue logic from other classes, so it can be replaced if
 * necessary, as we know it's slow.
 *
 * The HashMap construction is deliberate for speed considerations.
 */
@Singleton
class RecordMunger(
    private val columnNameMapper: ColumnNameMapper,
    private val coercer: Coercer,
    private val protobufConverter: ProtobufToAirbyteConverter
) : DataMunger {

    override fun transformForDest(msg: DestinationRecordRaw): Map<String, AirbyteValue> {
        return when (val source = msg.rawData) {
            is DestinationRecordProtobufSource -> transformProtobuf(msg, source)
            else -> transformEnrichedLegacy(msg)
        }
    }

    private fun transformEnrichedLegacy(msg: DestinationRecordRaw): HashMap<String, AirbyteValue> {
        val enriched =
            msg.asEnrichedDestinationRecordAirbyteValue(extractedAtAsTimestampWithTimezone = true)

        val munged = HashMap<String, AirbyteValue>()
        enriched.declaredFields.forEach { field ->
            val mappedKey =
                columnNameMapper.getMappedColumnName(msg.stream, field.key)
                    ?: field.key // fallback to original key

            val mappedValue = field.value.let { coercer.map(it) }.let { coercer.validate(it) }

            munged[mappedKey] = mappedValue.abValue
        }

        enriched.airbyteMetaFields.forEach { munged[it.key] = it.value.abValue }

        return munged
    }

    private fun transformProtobuf(
        msg: DestinationRecordRaw,
        source: DestinationRecordProtobufSource
    ): Map<String, AirbyteValue> {
        return protobufConverter.convertWithMetadata(msg, source)
    }
}
