/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.dataflow.transform.data

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.data.EnrichedAirbyteValue
import io.airbyte.cdk.load.data.NullValue
import io.airbyte.cdk.load.dataflow.state.PartitionKey
import io.airbyte.cdk.load.dataflow.state.stats.StateAdditionalStatsStore
import io.airbyte.cdk.load.dataflow.transform.ValidationResult
import io.airbyte.cdk.load.message.Meta
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMetaChange.Change
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMetaChange.Reason
import jakarta.inject.Singleton

/**
 * Handles validation results by appropriately performing actions such as truncating, nullifying, or
 * leaving values unchanged. Updates internal state statistics based on the applied actions.
 *
 * @constructor Creates an instance of `ValidationResultHandler` with the provided state statistics
 * store.
 * @param stateAdditionalStatsStore Store for tracking additional statistics related to state
 * changes.
 */
@Singleton
class ValidationResultHandler(private val stateAdditionalStatsStore: StateAdditionalStatsStore) {

    /**
     * Handles the provided validation result for a given value, partition, and stream.
     *
     * Depending on the validation result, the method may truncate the value, nullify it, or leave
     * it unchanged.
     *
     * @param partitionKey The partition key associated with the record.
     * @param stream The descriptor of the destination stream the value belongs to.
     * @param result The result of the validation process, which determines the action to take.
     * @param value The enriched Airbyte value to process based on the validation result.
     */
    fun handle(
        partitionKey: PartitionKey,
        stream: DestinationStream.Descriptor,
        result: ValidationResult,
        value: EnrichedAirbyteValue
    ) =
        when (result) {
            is ValidationResult.ShouldTruncate ->
                truncate(
                    partitionKey = partitionKey,
                    stream = stream,
                    value = value,
                    truncatedValue = result.truncatedValue,
                    reason = result.reason
                )
            is ValidationResult.ShouldNullify ->
                nullify(
                    partitionKey = partitionKey,
                    stream = stream,
                    value = value,
                    reason = result.reason
                )
            is ValidationResult.Valid -> value
        }

    /**
     * Nullifies the provided enriched Airbyte value by setting its value to null and recording the
     * change. Additionally, updates the state statistics for the nullification event.
     *
     * @param partitionKey The partition key associated with the record.
     * @param stream The descriptor of the destination stream that the value belongs to.
     * @param value The enriched Airbyte value to be nullified.
     * @param reason The reason for nullifying the value, defaulting to
     * DESTINATION_SERIALIZATION_ERROR.
     * @return The updated enriched Airbyte value with a nullified state and recorded change.
     */
    fun nullify(
        partitionKey: PartitionKey,
        stream: DestinationStream.Descriptor,
        value: EnrichedAirbyteValue,
        reason: Reason = Reason.DESTINATION_SERIALIZATION_ERROR
    ): EnrichedAirbyteValue {
        val nullChange = Meta.Change(field = value.name, change = Change.NULLED, reason = reason)
        value.abValue = NullValue
        value.changes.add(nullChange)
        stateAdditionalStatsStore.add(
            partitionKey = partitionKey,
            streamDescriptor = stream,
            metric = StateAdditionalStatsStore.ObservabilityMetrics.NULLED_VALUE_COUNT,
            value = 1.0
        )
        return value
    }

    /**
     * Truncates the provided enriched Airbyte value to adhere to a specified limit. Records the
     * truncation event as a change and updates the state statistics for the truncation event.
     *
     * @param partitionKey The partition key associated with the record.
     * @param stream The descriptor of the destination stream the value belongs to.
     * @param value The enriched Airbyte value that needs to be truncated.
     * @param truncatedValue The truncated version of the Airbyte value.
     * @param reason The reason for truncating the value, defaulting to
     * DESTINATION_RECORD_SIZE_LIMITATION.
     * @return The updated enriched Airbyte value with the truncation applied and recorded.
     */
    fun truncate(
        partitionKey: PartitionKey,
        stream: DestinationStream.Descriptor,
        value: EnrichedAirbyteValue,
        truncatedValue: AirbyteValue,
        reason: Reason = Reason.DESTINATION_RECORD_SIZE_LIMITATION
    ): EnrichedAirbyteValue {
        val truncateChange =
            Meta.Change(field = value.name, change = Change.TRUNCATED, reason = reason)
        value.abValue = truncatedValue
        value.changes.add(truncateChange)
        stateAdditionalStatsStore.add(
            partitionKey = partitionKey,
            streamDescriptor = stream,
            metric = StateAdditionalStatsStore.ObservabilityMetrics.TRUNCATED_VALUE_COUNT,
            value = 1.0
        )
        return value
    }
}
