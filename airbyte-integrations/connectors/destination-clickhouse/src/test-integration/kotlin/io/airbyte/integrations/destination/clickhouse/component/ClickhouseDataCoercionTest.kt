/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.clickhouse.component

import io.airbyte.cdk.load.component.DataCoercionNumberFixtures
import io.airbyte.cdk.load.component.DataCoercionSuite
import io.airbyte.cdk.load.component.DataCoercionTimestampNtzFixtures
import io.airbyte.cdk.load.component.DataCoercionTimestampTzFixtures
import io.airbyte.cdk.load.component.HIGH_PRECISION_TIMESTAMP
import io.airbyte.cdk.load.component.MAXIMUM_TIMESTAMP
import io.airbyte.cdk.load.component.MINIMUM_TIMESTAMP
import io.airbyte.cdk.load.component.OUT_OF_RANGE_TIMESTAMP
import io.airbyte.cdk.load.component.TableOperationsClient
import io.airbyte.cdk.load.component.TestTableOperationsClient
import io.airbyte.cdk.load.component.toArgs
import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.data.TimestampWithTimezoneValue
import io.airbyte.cdk.load.data.TimestampWithoutTimezoneValue
import io.airbyte.cdk.load.dataflow.transform.ValueCoercer
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMetaChange.Reason
import io.micronaut.test.extensions.junit5.annotation.MicronautTest
import java.time.LocalDateTime
import java.time.OffsetDateTime
import java.time.ZoneId
import java.time.ZoneOffset
import org.junit.jupiter.params.ParameterizedTest
import org.junit.jupiter.params.provider.MethodSource

@MicronautTest(environments = ["component"], resolveParameters = false)
class ClickhouseDataCoercionTest(
    override val coercer: ValueCoercer,
    override val opsClient: TableOperationsClient,
    override val testClient: TestTableOperationsClient
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

    @ParameterizedTest
    @MethodSource(
        "io.airbyte.integrations.destination.clickhouse.component.ClickhouseDataCoercionTest#timestampTz"
    )
    override fun `handle timestamptz values`(
        inputValue: AirbyteValue,
        expectedValue: Any?,
        expectedChangeReason: Reason?
    ) {
        super.`handle timestamptz values`(inputValue, expectedValue, expectedChangeReason)
    }

    @ParameterizedTest
    @MethodSource(
        "io.airbyte.integrations.destination.clickhouse.component.ClickhouseDataCoercionTest#timestampNtz"
    )
    override fun `handle timestampntz values`(
        inputValue: AirbyteValue,
        expectedValue: Any?,
        expectedChangeReason: Reason?
    ) {
        super.`handle timestampntz values`(inputValue, expectedValue, expectedChangeReason)
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
                    if (it.outputValue == null) {
                        // retain the change if we're nulling
                        it
                    } else {
                        // otherwise, either we're Valid or Truncating.
                        // in both cases, set the change to null.
                        it.copy(changeReason = null)
                    }
                }
                .toArgs()

        @JvmStatic
        fun timestampTz() =
            DataCoercionTimestampTzFixtures.commonWarehouse
                .map { fixture ->
                    when (fixture.name) {
                        // We use DateTime64(3), so truncate expected values to millis
                        HIGH_PRECISION_TIMESTAMP ->
                            fixture.copy(outputValue = "2025-01-23T01:01:00.123Z")
                        // Clickhouse timestamps can range from year 1900 <= it < 2300
                        MINIMUM_TIMESTAMP ->
                            fixture.copy(
                                inputValue = TimestampWithTimezoneValue("1900-01-01T00:00:00Z"),
                                outputValue = "1900-01-01T00:00:00Z",
                            )
                        MAXIMUM_TIMESTAMP ->
                            fixture.copy(
                                inputValue = TimestampWithTimezoneValue("2299-12-31T23:59:59.999Z"),
                                outputValue = "2299-12-31T23:59:59.999Z",
                            )
                        OUT_OF_RANGE_TIMESTAMP ->
                            fixture.copy(
                                inputValue = TimestampWithTimezoneValue("2300-01-01T00:00:00Z")
                            )
                        else -> fixture
                    }
                }
                // clickhouse client returns DateTime values as ZonedDateTime, so we need to do
                // the conversion here
                .map { fixture ->
                    fixture.copy(
                        outputValue =
                            fixture.outputValue?.let {
                                OffsetDateTime.parse(it as String)
                                    .atZoneSameInstant(ZoneId.of("UTC"))
                            }
                    )
                }
                .toArgs()

        /**
         * Basically identical to [timestampTz], but creates TimestampWithoutTimezoneValue instead
         * of TimestampWithTimezoneValue
         *
         * (note that we represent timestamp with/without timezone both as DateTime64, so the
         * returned value is always an OffsetDateTime)
         */
        @JvmStatic
        fun timestampNtz() =
            DataCoercionTimestampNtzFixtures.commonWarehouse
                .map { fixture ->
                    when (fixture.name) {
                        // We use DateTime64(3), so truncate expected values to millis
                        HIGH_PRECISION_TIMESTAMP ->
                            fixture.copy(outputValue = "2025-01-23T01:01:00.123")
                        // Clickhouse timestamps can range from year 1900 <= it < 2300
                        MINIMUM_TIMESTAMP ->
                            fixture.copy(
                                inputValue = TimestampWithoutTimezoneValue("1900-01-01T00:00:00"),
                                outputValue = "1900-01-01T00:00:00",
                            )
                        MAXIMUM_TIMESTAMP ->
                            fixture.copy(
                                inputValue =
                                    TimestampWithoutTimezoneValue("2299-12-31T23:59:59.999"),
                                outputValue = "2299-12-31T23:59:59.999",
                            )
                        OUT_OF_RANGE_TIMESTAMP ->
                            fixture.copy(
                                inputValue = TimestampWithoutTimezoneValue("2300-01-01T00:00:00")
                            )
                        else -> fixture
                    }
                }
                // clickhouse client returns DateTime values as ZonedDateTime, so we need to do
                // the conversion here
                .map { fixture ->
                    fixture.copy(
                        outputValue =
                            fixture.outputValue?.let {
                                LocalDateTime.parse(it as String)
                                    .atOffset(ZoneOffset.UTC)
                                    .atZoneSameInstant(ZoneId.of("UTC"))
                            }
                    )
                }
                .toArgs()
    }
}
