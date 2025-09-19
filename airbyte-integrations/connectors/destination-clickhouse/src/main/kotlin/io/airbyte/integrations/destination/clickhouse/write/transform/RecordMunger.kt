/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.clickhouse.write.transform

import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.data.UnionType
import io.airbyte.cdk.load.dataflow.transform.DataMunger
import io.airbyte.cdk.load.message.DestinationRecordRaw
import io.airbyte.cdk.load.orchestration.db.legacy_typing_deduping.TableCatalog
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
    private val catalogInfo: TableCatalog,
    private val coercer: ClickhouseCoercer,
) : DataMunger {
    override fun transformForDest(msg: DestinationRecordRaw): Map<String, AirbyteValue> {
        // this actually munges and coerces data
        val enriched =
            msg.asEnrichedDestinationRecordAirbyteValue(extractedAtAsTimestampWithTimezone = true)

        val munged = HashMap<String, AirbyteValue>()
        enriched.declaredFields.forEach { field ->
            val mappedKey = catalogInfo.getMappedColumnName(msg.stream, field.key)!!
            val fieldType = msg.schemaFields[field.key]!!

            var mappedValue =
                field.value
                    .let { if (fieldType.type is UnionType) coercer.toJsonStringValue(it) else it }
                    .let { coercer.validate(it) }

            mappedValue = coercer.validate(mappedValue)

            munged[mappedKey] = mappedValue.abValue
        }
        // must be called second so it picks up any meta changes from above
        enriched.airbyteMetaFields.forEach { munged[it.key] = it.value.abValue }

        return munged
    }
}
