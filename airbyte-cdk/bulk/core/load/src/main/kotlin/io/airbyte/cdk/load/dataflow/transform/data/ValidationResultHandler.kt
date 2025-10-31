/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.dataflow.transform.data

import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.data.EnrichedAirbyteValue
import io.airbyte.cdk.load.data.NullValue
import io.airbyte.cdk.load.dataflow.stats.MetricTracker
import io.airbyte.cdk.load.dataflow.transform.ValidationResult
import io.airbyte.cdk.load.message.Meta
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMetaChange.Change
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMetaChange.Reason
import jakarta.inject.Singleton

@Singleton
class ValidationResultHandler(private val metricTracker: MetricTracker) {

    fun handle(result: ValidationResult, value: EnrichedAirbyteValue) =
        when (result) {
            is ValidationResult.ShouldTruncate ->
                truncate(value, result.truncatedValue, result.reason)
            is ValidationResult.ShouldNullify -> nullify(value, result.reason)
            is ValidationResult.Valid -> value
        }

    /**
     * Creates a nullified version of this value with the specified reason.
     *
     * @param value The [EnrichedAirbyteValue] to nullify
     * @param reason The [Reason] for nullification, defaults to DESTINATION_SERIALIZATION_ERROR
     *
     * @return The nullified [EnrichedAirbyteValue].
     */
    fun nullify(
        value: EnrichedAirbyteValue,
        reason: Reason = Reason.DESTINATION_SERIALIZATION_ERROR
    ): EnrichedAirbyteValue {
        val nullChange = Meta.Change(field = value.name, change = Change.NULLED, reason = reason)
        value.abValue = NullValue
        value.changes.add(nullChange)
        metricTracker.add("NulledValueCount", 1.0)
        return value
    }

    /**
     * Creates a truncated version of this value with the specified reason and new value.
     *
     * @param value The original [EnrichedAirbyteValue] that is to be truncated
     * @param truncatedValue The new, truncated value to use
     * @param reason The [Reason] for truncation, defaults to DESTINATION_RECORD_SIZE_LIMITATION
     *
     * @return The truncated [EnrichedAirbyteValue].
     */
    fun truncate(
        value: EnrichedAirbyteValue,
        truncatedValue: AirbyteValue,
        reason: Reason = Reason.DESTINATION_RECORD_SIZE_LIMITATION
    ): EnrichedAirbyteValue {
        val truncateChange =
            Meta.Change(field = value.name, change = Change.TRUNCATED, reason = reason)
        value.abValue = truncatedValue
        value.changes.add(truncateChange)
        metricTracker.add("TruncatedValueCount", 1.0)
        return value
    }
}
