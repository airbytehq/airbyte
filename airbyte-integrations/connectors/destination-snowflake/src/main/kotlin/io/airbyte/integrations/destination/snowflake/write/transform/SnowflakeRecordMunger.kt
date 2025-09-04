/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.write.transform

import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.dataflow.transform.DataMunger
import io.airbyte.cdk.load.message.DestinationRecordRaw
import io.airbyte.cdk.load.orchestration.db.legacy_typing_deduping.TableCatalog
import jakarta.inject.Singleton

@Singleton
class SnowflakeRecordMunger(
    private val catalogInfo: TableCatalog,
) : DataMunger {
    override fun transformForDest(msg: DestinationRecordRaw): Map<String, AirbyteValue> {
        // this actually munges and coerces data
        val enriched =
            msg.asEnrichedDestinationRecordAirbyteValue(extractedAtAsTimestampWithTimezone = true)

        val munged =
            enriched.declaredFields.entries
                .associate { field ->
                    val mappedKey = catalogInfo.getMappedColumnName(msg.stream, field.key)!!

                    // TODO do any required data conversion/coercion here

                    mappedKey to field.value.abValue
                }
                .toMutableMap()

        // must be called second so it picks up any meta changes from above
        enriched.airbyteMetaFields.forEach { munged[it.key] = it.value.abValue }

        return munged
    }
}
