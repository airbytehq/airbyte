/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.dataflow.transform

import io.airbyte.cdk.load.data.AirbyteType
import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.data.EnrichedAirbyteValue

/**
 * Interface for destination-specific field coercion and type representation.
 *
 * This interface provides three main capabilities for destinations:
 * 1. **Type Representation Override**: Control how Airbyte types are converted from protobuf
 * 2. **Field Mapping**: Transform values after initial conversion
 * 3. **Field Validation**: Apply destination-specific constraints and validation
 *
 * The methods are called in this order during conversion:
 * 1. `representAs()` - during protobuf extraction to override default type representation
 * 2. `map()` - after initial conversion to apply transformations
 * 3. `validate()` - final step to apply constraints and validation
 */
interface Coercer {
    /**
     * Overrides how specific Airbyte types should be represented as AirbyteValue instances.
     *
     * This is called during the protobuf extraction phase, before any value is created. It allows
     * destinations to completely change the target representation of a type.
     *
     * **Common Use Cases:**
     * - Convert all temporal types to strings for destinations that don't support native dates
     * - Convert complex types (arrays, objects) to JSON strings
     * - Convert numbers to strings for destinations with limited numeric type support
     *
     * **Order of Operations:**
     * 1. Extract raw value from protobuf (e.g., `protobufValue.timeWithoutTimezone`)
     * 2. Check `representAs()` for type override
     * 3. Create AirbyteValue of the specified target class
     * 4. Apply `map()` and `validate()`
     *
     * @param airbyteType The original Airbyte type from the schema
     * @return The target AirbyteValue class to use instead of the default, or null for default
     * behavior
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
     * Applies destination-specific transformations to an enriched Airbyte value.
     *
     * This method is called after the initial AirbyteValue has been created (potentially using a
     * type override from `representAs()`). Use this for value transformations that depend on the
     * actual data content.
     *
     * **Common Use Cases:**
     * - Convert complex objects to JSON strings
     * - Apply format transformations (e.g., date format changes)
     * - Normalize string values (trim, case conversion)
     * - Apply unit conversions
     *
     * **Important Notes:**
     * - This method can modify the `abValue` property of the EnrichedAirbyteValue
     * - Changes made here affect the final output to the destination
     * - Consider performance impact for high-volume transformations
     *
     * @param value The enriched Airbyte value containing the converted data and metadata
     * @return The transformed EnrichedAirbyteValue (often the same instance, modified in-place)
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
     * Validates an enriched Airbyte value against destination-specific constraints.
     *
     * This is the final step in the coercion process. Use this to apply destination constraints
     * such as size limits, range checks, format validation, etc. Values that fail validation should
     * typically be nullified with appropriate metadata.
     *
     * **Common Use Cases:**
     * - Size limits (string length, numeric range, date range)
     * - Format validation (email, URL, phone number patterns)
     * - Destination-specific constraints (reserved keywords, encoding issues)
     * - Data quality checks
     *
     * **Best Practices:**
     * - Use `value.nullify(reason)` for validation failures
     * - Add descriptive metadata about why validation failed
     * - Log validation issues for monitoring and debugging
     *
     * @param value The enriched Airbyte value to validate
     * @return The validated EnrichedAirbyteValue, potentially nullified if validation fails
     *
     * @example
     * ```kotlin
     * override fun validate(value: EnrichedAirbyteValue): EnrichedAirbyteValue {
     *     when (val abValue = value.abValue) {
     *         is StringValue -> {
     *             if (abValue.value.length > MAX_STRING_LENGTH) {
     *                 value.nullify(
     *                     AirbyteRecordMessageMetaChange.Reason.DESTINATION_FIELD_SIZE_LIMITATION
     *                 )
     *             }
     *         }
     *         is IntegerValue -> {
     *             if (abValue.value > MAX_INTEGER) {
     *                 value.nullify(
     *                     AirbyteRecordMessageMetaChange.Reason.DESTINATION_FIELD_SIZE_LIMITATION
     *                 )
     *             }
     *         }
     *     }
     *     return value
     * }
     * ```
     */
    fun validate(value: EnrichedAirbyteValue): EnrichedAirbyteValue
}
