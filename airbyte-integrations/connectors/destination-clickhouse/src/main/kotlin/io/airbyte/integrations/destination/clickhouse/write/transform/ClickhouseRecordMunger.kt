/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.clickhouse.write.transform

import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.dataflow.transform.DataMunger
import io.airbyte.cdk.load.dataflow.transform.ProtobufToAirbyteConverter
import io.airbyte.cdk.load.message.DestinationRecordProtobufSource
import io.airbyte.cdk.load.message.DestinationRecordRaw
import io.airbyte.cdk.load.orchestration.db.legacy_typing_deduping.TableCatalog
import jakarta.inject.Singleton
import kotlin.collections.set

/*
 * Munges values and keys into a simple map form. Encapsulates
 * EnrichedAirbyteValue logic from other classes, so it can be replaced if
 * necessary, as we know it's slow.
 *
 * The HashMap construction is deliberate for speed considerations.
 */
@Singleton
class ClickhouseRecordMunger(
    private val catalogInfo: TableCatalog,
    private val coercer: ClickhouseCoercer,
) : DataMunger {
    private val protobufConverter = ProtobufToAirbyteConverter(coercer)
    override fun transformForDest(msg: DestinationRecordRaw): Map<String, AirbyteValue> {
        return when (val source = msg.rawData) {
            is DestinationRecordProtobufSource -> transformProtobuf(msg, source)
            else -> transformEnrichedLegacy(msg)
        }
    }

    private fun transformEnrichedLegacy(msg: DestinationRecordRaw): HashMap<String, AirbyteValue> {
        // this actually munges and coerces data
        val enriched =
            msg.asEnrichedDestinationRecordAirbyteValue(extractedAtAsTimestampWithTimezone = true)

        val munged = HashMap<String, AirbyteValue>()
        enriched.declaredFields.forEach { field ->
            val mappedKey = catalogInfo.getMappedColumnName(msg.stream, field.key)!!

            var mappedValue = field.value.let { coercer.map(it) }.let { coercer.validate(it) }

            munged[mappedKey] = mappedValue.abValue
        }
        // must be called second so it picks up any meta changes from above
        enriched.airbyteMetaFields.forEach { munged[it.key] = it.value.abValue }

        return munged
    }

    private fun transformProtobuf(
        msg: DestinationRecordRaw,
        source: DestinationRecordProtobufSource
    ): Map<String, AirbyteValue> {
        return protobufConverter.convertWithMetadata(msg, source) { stream, fieldName ->
            catalogInfo.getMappedColumnName(stream, fieldName)
        }
    }
}
