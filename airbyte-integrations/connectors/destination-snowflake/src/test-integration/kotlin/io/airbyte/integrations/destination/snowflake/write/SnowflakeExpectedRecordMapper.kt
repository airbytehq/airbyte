/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.write

import io.airbyte.cdk.load.data.AirbyteType
import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.data.EnrichedAirbyteValue
import io.airbyte.cdk.load.data.NullValue
import io.airbyte.cdk.load.data.ObjectValue
import io.airbyte.cdk.load.data.StringValue
import io.airbyte.cdk.load.data.TimeWithTimezoneValue
import io.airbyte.cdk.load.dataflow.transform.ValidationResult
import io.airbyte.cdk.load.message.Meta
import io.airbyte.cdk.load.test.util.ExpectedRecordMapper
import io.airbyte.cdk.load.test.util.OutputRecord
import io.airbyte.integrations.destination.snowflake.db.toSnowflakeCompatibleName
import io.airbyte.integrations.destination.snowflake.write.transform.SnowflakeValueCoercer
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMetaChange
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMetaChange.Change
import io.mockk.every
import io.mockk.mockk

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
                mappedData = mappedData.values,
                airbyteMetadata = expectedRecord.airbyteMeta
            )
        return expectedRecord.copy(data = mappedData, airbyteMeta = mappedAirbyteMetadata)
    }

    private fun mapAirbyteValue(value: AirbyteValue): AirbyteValue {
        val validationResult =
            SnowflakeValueCoercer(mockk { every { legacyRawTablesOnly } returns false })
                .validate(
                    EnrichedAirbyteValue(
                        value,
                        value.airbyteType,
                        name = "unused",
                        airbyteMetaField = null,
                    )
                )
        return when (validationResult) {
            is ValidationResult.ShouldNullify -> NullValue
            is ValidationResult.ShouldTruncate -> validationResult.truncatedValue
            ValidationResult.Valid ->
                when (value) {
                    is TimeWithTimezoneValue -> StringValue(value.value.toString())
                    else -> value
                }
        }
    }

    internal fun mapAirbyteMetadata(
        originalData: ObjectValue,
        mappedData: LinkedHashMap<String, AirbyteValue>,
        airbyteMetadata: OutputRecord.Meta?
    ): OutputRecord.Meta? {
        // Convert all fields to uppercase to match what comes out of the database
        val originalDataValues =
            originalData.values.entries.associate { it.key.uppercase() to it.value }

        val nullValues =
        // Find all values that the test has converted to a NullValue because the actual
        // value will fail the validation performed by the SnowflakeValueCoercer at runtime.
        // This excludes any "_AB" prefixed metadata columns or any columns that are already
        // null in the input data for the test.
        mappedData.entries
                // convert back to schema representation
                .filter {
                    !it.key.startsWith("_AB") &&
                        it.value is NullValue &&
                        originalDataValues[it.key] != NullValue
                }

        return if (nullValues.isNotEmpty()) {
            // Create a Set of existing change field names for O(1) lookup performance
            val existingChangeFields =
                airbyteMetadata?.changes?.map(metaChangeMapper)?.map { it.field }?.toSet()
                    ?: emptySet()

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
            val existingChanges: List<Meta.Change> =
                airbyteMetadata?.changes?.map(metaChangeMapper) ?: emptyList()

            airbyteMetadata?.copy(changes = changes + existingChanges)
                ?: OutputRecord.Meta(changes = changes, syncId = null)
        } else {
            airbyteMetadata?.copy(changes = airbyteMetadata.changes.map(metaChangeMapper))
        }
    }

    private val metaChangeMapper: (Meta.Change) -> Meta.Change = { change ->
        Meta.Change(
            field = change.field.uppercase(),
            reason = change.reason,
            change = change.change
        )
    }
}
