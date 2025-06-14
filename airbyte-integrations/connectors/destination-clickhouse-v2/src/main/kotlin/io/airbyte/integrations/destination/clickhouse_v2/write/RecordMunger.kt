package io.airbyte.integrations.destination.clickhouse_v2.write

import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.message.DestinationRecordRaw
import io.airbyte.cdk.load.orchestration.db.legacy_typing_deduping.TableCatalog
import jakarta.inject.Singleton

@Singleton
class RecordMunger(
    private val catalogInfo: TableCatalog,
) {
    fun transformForDest(record: DestinationRecordRaw): Map<String, AirbyteValue> {
        // this actually munges and coerces data
        val enriched = record.asEnrichedDestinationRecordAirbyteValue(
            extractedAtAsTimestampWithTimezone = true
        )

        val columnMapping = catalogInfo[record.stream]!!.columnNameMapping

        return buildMap {
            enriched.declaredFields.forEach {
                put(columnMapping[it.key]!!, it.value.abValue)
            }
            enriched.airbyteMetaFields.forEach {
                put(it.key, it.value.abValue)
            }
        }
    }
}
