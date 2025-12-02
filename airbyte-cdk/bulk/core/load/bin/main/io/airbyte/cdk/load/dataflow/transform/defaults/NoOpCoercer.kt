/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.dataflow.transform.defaults

import io.airbyte.cdk.load.data.EnrichedAirbyteValue
import io.airbyte.cdk.load.dataflow.transform.ValidationResult
import io.airbyte.cdk.load.dataflow.transform.ValueCoercer
import io.micronaut.context.annotation.Secondary
import jakarta.inject.Singleton

/*
 * Default implementation of the ValueCoercer. If your destination needs destination-specific
 * coercion or validation, create your own ValueCoercer implementation in your destination.
 */
@Singleton
@Secondary
class NoOpCoercer : ValueCoercer {
    override fun map(value: EnrichedAirbyteValue): EnrichedAirbyteValue = value

    override fun validate(value: EnrichedAirbyteValue): ValidationResult = ValidationResult.Valid
}
