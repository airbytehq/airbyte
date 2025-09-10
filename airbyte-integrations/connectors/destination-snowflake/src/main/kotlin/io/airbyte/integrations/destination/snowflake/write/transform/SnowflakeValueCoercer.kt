/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.write.transform

import io.airbyte.cdk.load.data.EnrichedAirbyteValue
import io.airbyte.cdk.load.dataflow.transform.ValueCoercer
import jakarta.inject.Singleton

@Singleton
class SnowflakeValueCoercer : ValueCoercer {
    override fun map(value: EnrichedAirbyteValue): EnrichedAirbyteValue {
        // TODO implement any type mapping here, like union to json string
        return value
    }

    override fun validate(value: EnrichedAirbyteValue): EnrichedAirbyteValue {
        // TODO check value conforms with snowflake limits, like integer size, string size, etc
        return value
    }
}
