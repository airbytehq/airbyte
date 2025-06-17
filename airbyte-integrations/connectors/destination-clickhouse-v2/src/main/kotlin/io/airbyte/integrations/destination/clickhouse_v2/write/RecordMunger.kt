/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.clickhouse_v2.write

import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.message.DestinationRecordRaw
import io.airbyte.cdk.load.orchestration.db.legacy_typing_deduping.TableCatalog
import jakarta.inject.Singleton

/*
 * Munges values and keys into a simple map form. Encapsulates
 * EnrichedAirybteValue logic from other classes, so it can be replaced if
 * necessary, as we know it's slow.
 *
 * The HashMap construction is deliberate for speed considerations.
 */
@Singleton
class RecordMunger(
    private val catalogInfo: TableCatalog,
) {
    fun transformForDest(record: DestinationRecordRaw): Map<String, AirbyteValue> {
        // this actually munges and coerces data
        val enriched =
            record.asEnrichedDestinationRecordAirbyteValue(
                extractedAtAsTimestampWithTimezone = true
            )

        val munged = HashMap<String, AirbyteValue>()
        enriched.declaredFields.forEach {
            val mappedKey = catalogInfo.getMappedColumnName(record.stream, it.key)!!
            munged[mappedKey] = it.value.abValue
        }
        enriched.airbyteMetaFields.forEach { munged[it.key] = it.value.abValue }

        return munged
    }
}
