/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.component

import io.airbyte.cdk.load.component.DataCoercionIntegerFixtures
import io.airbyte.cdk.load.component.DataCoercionSuite
import io.airbyte.cdk.load.component.TableOperationsClient
import io.airbyte.cdk.load.component.TestTableOperationsClient
import io.airbyte.cdk.load.component.toArgs
import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.dataflow.transform.ValueCoercer
import io.micronaut.test.extensions.junit5.annotation.MicronautTest
import org.junit.jupiter.api.parallel.Execution
import org.junit.jupiter.api.parallel.ExecutionMode
import org.junit.jupiter.params.ParameterizedTest
import org.junit.jupiter.params.provider.MethodSource

@MicronautTest(environments = ["component"], resolveParameters = false)
@Execution(ExecutionMode.CONCURRENT)
class SnowflakeDataCoercionTest(
    override val coercer: ValueCoercer,
    override val opsClient: TableOperationsClient,
    override val testClient: TestTableOperationsClient,
) : DataCoercionSuite {
    override val columnNameMapping = SnowflakeComponentTestFixtures.testMapping
    override val airbyteMetaColumnMapping = SnowflakeComponentTestFixtures.airbyteMetaColumnMapping

    @ParameterizedTest
    @MethodSource(
        "io.airbyte.integrations.destination.snowflake.component.SnowflakeDataCoercionTest#integers"
    )
    override fun `handle integer values`(inputValue: AirbyteValue, expectedValue: Any?) {
        super.`handle integer values`(inputValue, expectedValue)
    }

    companion object {
        /**
         * Snowflake does two interesting things when querying a `NUMERIC(38, 0)` column:
         * 1. Most values are returned as BigDecimal, rather than BigInteger
         * 2. Values within the `Long` range are returned as Long
         *
         * Otherwise, it's a totally standard NUMERIC(38, 0) column, so we can just modify the
         * numeric38_0 fixture.
         */
        @JvmStatic
        fun integers() =
            DataCoercionIntegerFixtures.numeric38_0
                .map { (input, output) ->
                    input to
                        output?.let {
                            try {
                                // try to convert to long
                                it.longValueExact()
                            } catch (_: Exception) {
                                // if we can't (probably because the value is too large),
                                // convert to bigdecimal
                                it.toBigDecimal()
                            }
                        }
                }
                .toArgs()
    }
}
