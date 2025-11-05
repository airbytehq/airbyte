/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.dataflow.transform.data

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.data.EnrichedAirbyteValue
import io.airbyte.cdk.load.data.NullValue
import io.airbyte.cdk.load.dataflow.stats.MetricTracker
import io.airbyte.cdk.load.dataflow.stats.ObservabilityMetrics
import io.airbyte.cdk.load.dataflow.transform.ValidationResult
import io.airbyte.cdk.load.message.Meta
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMetaChange.Change
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMetaChange.Reason
import jakarta.inject.Singleton

@Singleton
class ValidationResultHandler(private val metricTracker: MetricTracker) {

    /**
     * Processes an `EnrichedAirbyteValue` based on its corresponding `ValidationResult`. The method
     * handles three cases:
     * - If the result requires truncation, the value is truncated using the `truncate` method.
     * - If the result requires nullification, the value is nullified using the `nullify` method.
     * - If the result is valid, the original value is returned.
     *
     * @param stream The descriptor of the destination stream where the value belongs.
     * @param result The validation result indicating how the value should be handled.
     * @param value The enriched Airbyte value to process based on the validation result.
     */
    fun handle(
        stream: DestinationStream.Descriptor,
        result: ValidationResult,
        value: EnrichedAirbyteValue
    ) =
        when (result) {
            is ValidationResult.ShouldTruncate ->
                truncate(
                    stream = stream,
                    value = value,
                    truncatedValue = result.truncatedValue,
                    reason = result.reason
                )
            is ValidationResult.ShouldNullify ->
                nullify(stream = stream, value = value, reason = result.reason)
            is ValidationResult.Valid -> value
        }

    /**
     * Creates a nullified version of this value with the specified reason.
     *
     * @param stream The [DestinationStream.Descriptor] for the stream that this nulled value
     * belongs to.
     * @param value The [EnrichedAirbyteValue] to nullify
     * @param reason The [Reason] for nullification, defaults to DESTINATION_SERIALIZATION_ERROR
     *
     * @return The nullified [EnrichedAirbyteValue].
     */
    fun nullify(
        stream: DestinationStream.Descriptor,
        value: EnrichedAirbyteValue,
        reason: Reason = Reason.DESTINATION_SERIALIZATION_ERROR
    ): EnrichedAirbyteValue {
        val nullChange = Meta.Change(field = value.name, change = Change.NULLED, reason = reason)
        value.abValue = NullValue
        value.changes.add(nullChange)
        metricTracker.add(stream, ObservabilityMetrics.NULLED_VALUE_COUNT, 1.0)
        return value
    }

    /**
     * Creates a truncated version of this value with the specified reason and new value.
     *
     * @param stream The [DestinationStream.Descriptor] for the stream that this truncated value
     * belongs to.
     * @param value The original [EnrichedAirbyteValue] that is to be truncated
     * @param truncatedValue The new, truncated value to use
     * @param reason The [Reason] for truncation, defaults to DESTINATION_RECORD_SIZE_LIMITATION
     *
     * @return The truncated [EnrichedAirbyteValue].
     */
    fun truncate(
        stream: DestinationStream.Descriptor,
        value: EnrichedAirbyteValue,
        truncatedValue: AirbyteValue,
        reason: Reason = Reason.DESTINATION_RECORD_SIZE_LIMITATION
    ): EnrichedAirbyteValue {
        val truncateChange =
            Meta.Change(field = value.name, change = Change.TRUNCATED, reason = reason)
        value.abValue = truncatedValue
        value.changes.add(truncateChange)
        metricTracker.add(stream, ObservabilityMetrics.TRUNCATED_VALUE_COUNT, 1.0)
        return value
    }
}
