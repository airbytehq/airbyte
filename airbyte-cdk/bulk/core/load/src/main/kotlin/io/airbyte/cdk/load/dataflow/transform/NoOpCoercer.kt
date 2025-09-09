/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.dataflow.transform

import io.airbyte.cdk.load.data.EnrichedAirbyteValue
import io.micronaut.context.annotation.Secondary
import jakarta.inject.Singleton

@Singleton
@Secondary
class NoOpCoercer : Coercer {
    override fun map(value: EnrichedAirbyteValue): EnrichedAirbyteValue = value

    override fun validate(value: EnrichedAirbyteValue): EnrichedAirbyteValue = value
}
