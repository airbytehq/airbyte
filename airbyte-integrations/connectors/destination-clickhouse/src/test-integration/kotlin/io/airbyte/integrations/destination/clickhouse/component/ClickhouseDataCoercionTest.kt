/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.clickhouse.component

import io.airbyte.cdk.load.component.DataCoercionNumberFixtures
import io.airbyte.cdk.load.component.DataCoercionNumberFixtures.NEGATIVE_HIGH_PRECISION_FLOAT
import io.airbyte.cdk.load.component.DataCoercionNumberFixtures.POSITIVE_HIGH_PRECISION_FLOAT
import io.airbyte.cdk.load.component.DataCoercionNumberFixtures.SMALLEST_NEGATIVE_FLOAT32
import io.airbyte.cdk.load.component.DataCoercionNumberFixtures.SMALLEST_NEGATIVE_FLOAT64
import io.airbyte.cdk.load.component.DataCoercionNumberFixtures.SMALLEST_POSITIVE_FLOAT32
import io.airbyte.cdk.load.component.DataCoercionNumberFixtures.SMALLEST_POSITIVE_FLOAT64
import io.airbyte.cdk.load.component.DataCoercionSuite
import io.airbyte.cdk.load.component.TableOperationsClient
import io.airbyte.cdk.load.component.TestTableOperationsClient
import io.airbyte.cdk.load.component.toArgs
import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.dataflow.transform.ValueCoercer
import io.airbyte.cdk.load.schema.TableSchemaFactory
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMetaChange.Reason
import io.micronaut.test.extensions.junit5.annotation.MicronautTest
import org.junit.jupiter.params.ParameterizedTest
import org.junit.jupiter.params.provider.MethodSource

@MicronautTest(environments = ["component"], resolveParameters = false)
class ClickhouseDataCoercionTest(
    override val coercer: ValueCoercer,
    override val opsClient: TableOperationsClient,
    override val testClient: TestTableOperationsClient,
    override val schemaFactory: TableSchemaFactory,
) : DataCoercionSuite {
    @ParameterizedTest
    // We use clickhouse's Int64 type for integers
    @MethodSource("io.airbyte.cdk.load.component.DataCoercionIntegerFixtures#int64")
    override fun `handle integer values`(
        inputValue: AirbyteValue,
        expectedValue: Any?,
        expectedChangeReason: Reason?
    ) {
        super.`handle integer values`(inputValue, expectedValue, expectedChangeReason)
    }

    @ParameterizedTest
    @MethodSource(
        "io.airbyte.integrations.destination.clickhouse.component.ClickhouseDataCoercionTest#numbers"
    )
    override fun `handle number values`(
        inputValue: AirbyteValue,
        expectedValue: Any?,
        expectedChangeReason: Reason?
    ) {
        super.`handle number values`(inputValue, expectedValue, expectedChangeReason)
    }

    companion object {
        /**
         * destination-clickhouse doesn't set a change reason when truncating high-precision numbers
         * (https://github.com/airbytehq/airbyte-internal-issues/issues/15401)
         */
        @JvmStatic
        fun numbers() =
            DataCoercionNumberFixtures.numeric38_9
                .map {
                    when (it.name) {
                        POSITIVE_HIGH_PRECISION_FLOAT,
                        NEGATIVE_HIGH_PRECISION_FLOAT,
                        SMALLEST_POSITIVE_FLOAT32,
                        SMALLEST_NEGATIVE_FLOAT32,
                        SMALLEST_POSITIVE_FLOAT64,
                        SMALLEST_NEGATIVE_FLOAT64 -> it.copy(changeReason = null)
                        else -> it
                    }
                }
                .toArgs()
    }
}
