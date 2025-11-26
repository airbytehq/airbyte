/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.clickhouse.component

import io.airbyte.cdk.load.component.DataCoercionSuite
import io.airbyte.cdk.load.component.TableOperationsClient
import io.airbyte.cdk.load.component.TestTableOperationsClient
import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.dataflow.transform.ValueCoercer
import io.micronaut.context.annotation.Property
import io.micronaut.test.extensions.junit5.annotation.MicronautTest
import org.junit.jupiter.params.ParameterizedTest
import org.junit.jupiter.params.provider.MethodSource

@MicronautTest(environments = ["component"], resolveParameters = false)
class ClickhouseDataCoercionTest(
    override val coercer: ValueCoercer,
    override val opsClient: TableOperationsClient,
    override val testClient: TestTableOperationsClient
) : DataCoercionSuite {
    // We use clickhouse's Int64 type for integers
    @Property(name = "foo", value = "bar")
    @ParameterizedTest
    @MethodSource("io.airbyte.cdk.load.component.DataCoercionIntegerFixtures#int64")
    override fun `handle integer values`(inputValue: AirbyteValue, expectedValue: Any?) {
        super.`handle integer values`(inputValue, expectedValue)
    }

    @ParameterizedTest
    @MethodSource("io.airbyte.cdk.load.component.DataCoercionNumberFixtures#numeric38_9")
    override fun `handle number values`(inputValue: AirbyteValue, expectedValue: Any?) {
        super.`handle number values`(inputValue, expectedValue)
    }
}
