/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.dataflow.transform

import io.airbyte.cdk.load.data.AirbyteType
import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.data.EnrichedAirbyteValue
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMetaChange

/**
 * Interface for destination-specific field coercion and type representation.
 *
 * Methods are called in this order during conversion:
 * 1. `representAs()` - override default type representation during protobuf extraction
 * 2. `map()` - transform values after initial conversion
 * 3. `validate()` - apply constraints and validation
 */
interface ValueCoercer {
    /**
     * Overrides how specific Airbyte types should be represented as AirbyteValue instances. Called
     * during protobuf extraction phase before value creation.
     *
     * @param airbyteType The original Airbyte type from the schema
     * @return The target AirbyteValue class to use, or null for default behavior
     *
     * @example
     * ```kotlin
     * override fun representAs(airbyteType: AirbyteType): Class<out AirbyteValue>? {
     *     return when (airbyteType) {
     *         // Convert all time types to strings
     *         is TimeTypeWithoutTimezone -> StringValue::class.java
     *         is TimestampTypeWithTimezone -> StringValue::class.java
     *
     *         // Convert arrays and objects to JSON strings
     *         is ArrayType, is ObjectType -> StringValue::class.java
     *
     *         // Use default representation for other types
     *         else -> null
     *     }
     * }
     * ```
     */
    fun representAs(airbyteType: AirbyteType): Class<out AirbyteValue>? = null

    /**
     * Applies transformations to values after initial conversion. Called after AirbyteValue
     * creation for data-dependent transformations.
     *
     * @param value The enriched Airbyte value to transform
     * @return The transformed EnrichedAirbyteValue
     *
     * @example
     * ```kotlin
     * override fun map(value: EnrichedAirbyteValue): EnrichedAirbyteValue {
     *     return when (value.type) {
     *         is UnionType -> {
     *             // Convert union types to JSON strings
     *             value.abValue = StringValue(value.abValue.toString())
     *             value
     *         }
     *         else -> value // No transformation needed
     *     }
     * }
     * ```
     */
    fun map(value: EnrichedAirbyteValue): EnrichedAirbyteValue

    /**
     * Validates values against destination-specific constraints. Final step in coercion process -
     * nullify values that fail validation.
     *
     * @param value The enriched Airbyte value to validate
     * @return The [ValidationResult] indicating whether the value is valid or not, and if so, why
     *
     * @example
     * ```kotlin
     * override fun validate(value: EnrichedAirbyteValue): ValidationResult =
     *     when (val abValue = value.abValue) {
     *         is StringValue -> {
     *             if (abValue.value.length > MAX_STRING_LENGTH) {
     *               ShouldNullify(AirbyteRecordMessageMetaChange.Reason.DESTINATION_FIELD_SIZE_LIMITATION)
     *             } else {
     *               Valid
     *             }
     *         }
     *         is IntegerValue -> {
     *             if (abValue.value > MAX_INTEGER) {
     *               ShouldNullify(AirbyteRecordMessageMetaChange.Reason.DESTINATION_FIELD_SIZE_LIMITATION)
     *             } else {
     *               Valid
     *             }
     *         }
     *     }
     * ```
     */
    fun validate(value: EnrichedAirbyteValue): ValidationResult
}

/** Result of a value validation check via the [ValueCoercer.validate] method. */
sealed interface ValidationResult {
    /** Value is valid, no action needed */
    data object Valid : ValidationResult

    /** Value should be nullified with the given reason */
    data class ShouldNullify(val reason: AirbyteRecordMessageMetaChange.Reason) : ValidationResult

    /** Value should be replaced with the new, truncated value and reason */
    data class ShouldTruncate(
        val truncatedValue: AirbyteValue,
        val reason: AirbyteRecordMessageMetaChange.Reason
    ) : ValidationResult
}
