/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.write

import io.airbyte.cdk.load.data.AirbyteType
import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.data.ArrayValue
import io.airbyte.cdk.load.data.NullValue
import io.airbyte.cdk.load.data.ObjectValue
import io.airbyte.cdk.load.data.StringValue
import io.airbyte.cdk.load.data.TimeWithTimezoneValue
import io.airbyte.cdk.load.data.json.toJson
import io.airbyte.cdk.load.message.Meta
import io.airbyte.cdk.load.test.util.ExpectedRecordMapper
import io.airbyte.cdk.load.test.util.OutputRecord
import io.airbyte.integrations.destination.snowflake.db.toSnowflakeCompatibleName
import io.airbyte.integrations.destination.snowflake.write.transform.isValid
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMetaChange
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMetaChange.Change
import kotlin.collections.component1
import kotlin.collections.component2

object SnowflakeExpectedRecordMapper : ExpectedRecordMapper {

    override fun mapRecord(expectedRecord: OutputRecord, schema: AirbyteType): OutputRecord {
        val mappedData =
            ObjectValue(
                expectedRecord.data.values
                    .mapValuesTo(linkedMapOf()) { (_, value) -> mapAirbyteValue(value) }
                    .mapKeysTo(linkedMapOf()) { it.key.toSnowflakeCompatibleName() }
            )

        val mappedAirbyteMetadata =
            mapAirbyteMetadata(
                originalData = expectedRecord.data,
                mappedData = mappedData,
                airbyteMetadata = expectedRecord.airbyteMeta
            )
        return expectedRecord.copy(data = mappedData, airbyteMeta = mappedAirbyteMetadata)
    }

    private fun mapAirbyteValue(value: AirbyteValue): AirbyteValue {
        return if (isValid(value)) {
            when (value) {
                is TimeWithTimezoneValue -> StringValue(value.value.toString())
                is ArrayValue,
                is ObjectValue -> StringValue(value.toJson().toPrettyString())
                else -> value
            }
        } else {
            NullValue
        }
    }

    internal fun mapAirbyteMetadata(
        originalData: ObjectValue,
        mappedData: ObjectValue,
        airbyteMetadata: OutputRecord.Meta?
    ): OutputRecord.Meta? {
        val nullValues =
        // Find all values that the test has converted to a NullValue because the actual
        // value will fail the validation performed by the SnowflakeValueCoercer at runtime.
        // This excludes any "_ab" prefixed metadata columns or any columns that are already
        // null in the input data for the test.
        mappedData.values.entries.filter {
                !it.key.startsWith("_ab") &&
                    it.value is NullValue &&
                    originalData.values[it.key] != NullValue
            }
        return if (nullValues.isNotEmpty()) {
            // Create a Set of existing change field names for O(1) lookup performance
            val existingChangeFields =
                airbyteMetadata?.changes?.map { it.field }?.toSet() ?: emptySet()

            val changes =
                nullValues
                    // If the field null-ed out by this mapper is already in the input metadata
                    // change list, ignore it.  Otherwise, add it to the collection of changes
                    // to synthesize the validation null-ing of the field.
                    .filter { (k, _) -> !existingChangeFields.contains(k) }
                    .map { (k, _) ->
                        Meta.Change(
                            field = k,
                            change = Change.NULLED,
                            reason =
                                AirbyteRecordMessageMetaChange.Reason
                                    .DESTINATION_FIELD_SIZE_LIMITATION
                        )
                    }
            airbyteMetadata?.copy(changes = changes + airbyteMetadata.changes)
                ?: OutputRecord.Meta(changes = changes, syncId = null)
        } else {
            airbyteMetadata
        }
    }
}
