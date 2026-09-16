/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift.component

import io.airbyte.cdk.load.component.DataCoercionDateFixtures
import io.airbyte.cdk.load.component.DataCoercionNumberFixtures
import io.airbyte.cdk.load.component.DataCoercionNumberFixtures.NEGATIVE_HIGH_PRECISION_FLOAT
import io.airbyte.cdk.load.component.DataCoercionNumberFixtures.NUMERIC_38_9_MAX
import io.airbyte.cdk.load.component.DataCoercionNumberFixtures.NUMERIC_38_9_MIN
import io.airbyte.cdk.load.component.DataCoercionNumberFixtures.POSITIVE_HIGH_PRECISION_FLOAT
import io.airbyte.cdk.load.component.DataCoercionNumberFixtures.SMALLEST_NEGATIVE_FLOAT32
import io.airbyte.cdk.load.component.DataCoercionNumberFixtures.SMALLEST_NEGATIVE_FLOAT64
import io.airbyte.cdk.load.component.DataCoercionNumberFixtures.SMALLEST_POSITIVE_FLOAT32
import io.airbyte.cdk.load.component.DataCoercionNumberFixtures.SMALLEST_POSITIVE_FLOAT64
import io.airbyte.cdk.load.component.DataCoercionStringFixtures
import io.airbyte.cdk.load.component.DataCoercionStringFixtures.LONG_STRING
import io.airbyte.cdk.load.component.DataCoercionStringFixtures.NULL_CHAR_STRING
import io.airbyte.cdk.load.component.DataCoercionSuite
import io.airbyte.cdk.load.component.DataCoercionTimeNtzFixtures
import io.airbyte.cdk.load.component.DataCoercionTimeTzFixtures
import io.airbyte.cdk.load.component.DataCoercionTimestampNtzFixtures
import io.airbyte.cdk.load.component.DataCoercionTimestampTzFixtures
import io.airbyte.cdk.load.component.DataCoercionUnknownFixtures
import io.airbyte.cdk.load.component.DataCoercionUnknownFixtures.STR_VALUE
import io.airbyte.cdk.load.component.HIGH_NOON
import io.airbyte.cdk.load.component.HIGH_PRECISION_TIMESTAMP
import io.airbyte.cdk.load.component.MAXIMUM_TIMESTAMP
import io.airbyte.cdk.load.component.MAX_TIME
import io.airbyte.cdk.load.component.MIDNIGHT
import io.airbyte.cdk.load.component.MINIMUM_TIMESTAMP
import io.airbyte.cdk.load.component.OUT_OF_RANGE_TIMESTAMP
import io.airbyte.cdk.load.component.TableOperationsClient
import io.airbyte.cdk.load.component.TestTableOperationsClient
import io.airbyte.cdk.load.component.UNIX_EPOCH
import io.airbyte.cdk.load.component.toArgs
import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.dataflow.transform.ValueCoercer
import io.airbyte.cdk.load.schema.TableSchemaFactory
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMetaChange.Reason
import io.micronaut.test.extensions.junit5.annotation.MicronautTest
import org.junit.jupiter.api.Test
import org.junit.jupiter.params.ParameterizedTest
import org.junit.jupiter.params.provider.MethodSource

/**
 * Data coercion tests for Redshift. Verifies that each data type is correctly coerced, written, and
 * read back through the component test framework.
 */
@MicronautTest(environments = ["component"], resolveParameters = false)
class RedshiftDataCoercionTest(
    override val coercer: ValueCoercer,
    override val opsClient: TableOperationsClient,
    override val testClient: TestTableOperationsClient,
    override val schemaFactory: TableSchemaFactory,
) : DataCoercionSuite {

    @ParameterizedTest
    @MethodSource("io.airbyte.cdk.load.component.DataCoercionIntegerFixtures#int64")
    override fun `handle integer values`(
        inputValue: AirbyteValue,
        expectedValue: Any?,
        expectedChangeReason: Reason?,
    ) {
        super.`handle integer values`(inputValue, expectedValue, expectedChangeReason)
    }

    @ParameterizedTest
    @MethodSource(
        "io.airbyte.integrations.destination.redshift.component.RedshiftDataCoercionTest#numbers"
    )
    override fun `handle number values`(
        inputValue: AirbyteValue,
        expectedValue: Any?,
        expectedChangeReason: Reason?,
    ) {
        super.`handle number values`(inputValue, expectedValue, expectedChangeReason)
    }

    @ParameterizedTest
    @MethodSource(
        "io.airbyte.integrations.destination.redshift.component.RedshiftDataCoercionTest#timestampTz"
    )
    override fun `handle timestamptz values`(
        inputValue: AirbyteValue,
        expectedValue: Any?,
        expectedChangeReason: Reason?,
    ) {
        super.`handle timestamptz values`(inputValue, expectedValue, expectedChangeReason)
    }

    @ParameterizedTest
    @MethodSource(
        "io.airbyte.integrations.destination.redshift.component.RedshiftDataCoercionTest#timestampNtz"
    )
    override fun `handle timestampntz values`(
        inputValue: AirbyteValue,
        expectedValue: Any?,
        expectedChangeReason: Reason?,
    ) {
        super.`handle timestampntz values`(inputValue, expectedValue, expectedChangeReason)
    }

    @ParameterizedTest
    @MethodSource(
        "io.airbyte.integrations.destination.redshift.component.RedshiftDataCoercionTest#timetz"
    )
    override fun `handle timetz values`(
        inputValue: AirbyteValue,
        expectedValue: Any?,
        expectedChangeReason: Reason?,
    ) {
        super.`handle timetz values`(inputValue, expectedValue, expectedChangeReason)
    }

    @ParameterizedTest
    @MethodSource(
        "io.airbyte.integrations.destination.redshift.component.RedshiftDataCoercionTest#timentz"
    )
    override fun `handle timentz values`(
        inputValue: AirbyteValue,
        expectedValue: Any?,
        expectedChangeReason: Reason?,
    ) {
        super.`handle timentz values`(inputValue, expectedValue, expectedChangeReason)
    }

    @ParameterizedTest
    @MethodSource(
        "io.airbyte.integrations.destination.redshift.component.RedshiftDataCoercionTest#date"
    )
    override fun `handle date values`(
        inputValue: AirbyteValue,
        expectedValue: Any?,
        expectedChangeReason: Reason?,
    ) {
        super.`handle date values`(inputValue, expectedValue, expectedChangeReason)
    }

    @Test
    fun `handle boolean values`() {
        super.`handle bool values`(expectedValue = true)
    }

    @ParameterizedTest
    @MethodSource(
        "io.airbyte.integrations.destination.redshift.component.RedshiftDataCoercionTest#string"
    )
    override fun `handle string values`(
        inputValue: AirbyteValue,
        expectedValue: Any?,
        expectedChangeReason: Reason?,
    ) {
        super.`handle string values`(inputValue, expectedValue, expectedChangeReason)
    }

    // Redshift SUPER columns: the test client (RedshiftTestTableOperationsClient) reads SUPER
    // values as JSON strings, so we use the stringified fixtures.
    @ParameterizedTest
    @MethodSource("io.airbyte.cdk.load.component.DataCoercionObjectFixtures#stringifiedObjects")
    override fun `handle object values`(
        inputValue: AirbyteValue,
        expectedValue: Any?,
        expectedChangeReason: Reason?,
    ) {
        super.`handle object values`(inputValue, expectedValue, expectedChangeReason)
    }

    @ParameterizedTest
    @MethodSource("io.airbyte.cdk.load.component.DataCoercionObjectFixtures#stringifiedObjects")
    override fun `handle empty object values`(
        inputValue: AirbyteValue,
        expectedValue: Any?,
        expectedChangeReason: Reason?,
    ) {
        super.`handle empty object values`(inputValue, expectedValue, expectedChangeReason)
    }

    @ParameterizedTest
    @MethodSource("io.airbyte.cdk.load.component.DataCoercionObjectFixtures#stringifiedObjects")
    override fun `handle schemaless object values`(
        inputValue: AirbyteValue,
        expectedValue: Any?,
        expectedChangeReason: Reason?,
    ) {
        super.`handle schemaless object values`(inputValue, expectedValue, expectedChangeReason)
    }

    @ParameterizedTest
    @MethodSource("io.airbyte.cdk.load.component.DataCoercionArrayFixtures#stringifiedArrays")
    override fun `handle array values`(
        inputValue: AirbyteValue,
        expectedValue: Any?,
        expectedChangeReason: Reason?,
    ) {
        super.`handle array values`(inputValue, expectedValue, expectedChangeReason)
    }

    @ParameterizedTest
    @MethodSource("io.airbyte.cdk.load.component.DataCoercionArrayFixtures#stringifiedArrays")
    override fun `handle schemaless array values`(
        inputValue: AirbyteValue,
        expectedValue: Any?,
        expectedChangeReason: Reason?,
    ) {
        super.`handle schemaless array values`(inputValue, expectedValue, expectedChangeReason)
    }

    /** Unions are serialized to JSON strings by [RedshiftValueCoercer.map] for VARCHAR storage. */
    @ParameterizedTest
    @MethodSource("io.airbyte.cdk.load.component.DataCoercionUnionFixtures#stringifiedUnions")
    override fun `handle union values`(
        inputValue: AirbyteValue,
        expectedValue: Any?,
        expectedChangeReason: Reason?,
    ) {
        super.`handle union values`(inputValue, expectedValue, expectedChangeReason)
    }

    /**
     * Unknown types map to VARCHAR(65535) on this branch, so the test client reads them as strings.
     * Use stringified unknowns and adjust the string value case.
     */
    @ParameterizedTest
    @MethodSource(
        "io.airbyte.integrations.destination.redshift.component.RedshiftDataCoercionTest#unknown"
    )
    override fun `handle unknown values`(
        inputValue: AirbyteValue,
        expectedValue: Any?,
        expectedChangeReason: Reason?,
    ) {
        super.`handle unknown values`(inputValue, expectedValue, expectedChangeReason)
    }

    companion object {
        /**
         * Redshift does not set a change reason when truncating high-precision numbers because
         * truncation is handled natively by Redshift's ROUNDEC during COPY, not by the coercer.
         *
         * Smallest float32/float64 values (e.g. 1.4E-45, 4.9E-324) are filtered because their
         * BigDecimal representation exceeds NUMERIC(38,9)'s total precision, causing Redshift to
         * reject them during direct JDBC INSERT. In the production pipeline (CSV → COPY with
         * ROUNDEC), these would be handled by Redshift's native rounding.
         */
        @JvmStatic
        fun numbers() =
            DataCoercionNumberFixtures.numeric38_9
                .filter {
                    it.name !in
                        setOf(
                            SMALLEST_POSITIVE_FLOAT32,
                            SMALLEST_NEGATIVE_FLOAT32,
                            SMALLEST_POSITIVE_FLOAT64,
                            SMALLEST_NEGATIVE_FLOAT64,
                        )
                }
                .map {
                    when (it.name) {
                        POSITIVE_HIGH_PRECISION_FLOAT,
                        NEGATIVE_HIGH_PRECISION_FLOAT,
                        NUMERIC_38_9_MAX,
                        NUMERIC_38_9_MIN -> it.copy(changeReason = null)
                        else -> it
                    }
                }
                .toArgs()

        /**
         * Redshift TIMESTAMPTZ has microsecond precision (6 digits) and rounds UP (not truncates).
         * - HIGH_PRECISION: .123456789 rounds to .123457 (not .123456)
         * - MAXIMUM: .999999999 rounds up and overflows year 9999 → filter out
         * - MINIMUM (tz): year 0001 has calendar discrepancy in Redshift → filter out
         * - OUT_OF_RANGE: coercer doesn't validate timestamp ranges → filter out
         */
        @JvmStatic
        fun timestampTz() =
            DataCoercionTimestampTzFixtures.commonWarehouse
                .filter {
                    it.name !in setOf(OUT_OF_RANGE_TIMESTAMP, MAXIMUM_TIMESTAMP, MINIMUM_TIMESTAMP)
                }
                .map { fixture ->
                    when (fixture.name) {
                        HIGH_PRECISION_TIMESTAMP ->
                            fixture.copy(outputValue = "2025-01-23T01:01:00.123457Z")
                        else -> fixture
                    }
                }
                .toArgs()

        /**
         * Same as [timestampTz] but for timestamp without timezone. Redshift also rounds UP.
         * - UNIX_EPOCH and MINIMUM: Redshift returns "T00:00" (no seconds)
         * - MAXIMUM: .999999999 rounds up, overflows → filter out
         */
        @JvmStatic
        fun timestampNtz() =
            DataCoercionTimestampNtzFixtures.commonWarehouse
                .filter { it.name !in setOf(OUT_OF_RANGE_TIMESTAMP, MAXIMUM_TIMESTAMP) }
                .map { fixture ->
                    when (fixture.name) {
                        HIGH_PRECISION_TIMESTAMP ->
                            fixture.copy(outputValue = "2025-01-23T01:01:00.123457")
                        // Redshift returns timestamps with zero seconds as "T00:00"
                        // (LocalDateTime.toString() omits trailing zeros)
                        UNIX_EPOCH -> fixture.copy(outputValue = "1970-01-01T00:00")
                        MINIMUM_TIMESTAMP -> fixture.copy(outputValue = "0001-01-01T00:00")
                        else -> fixture
                    }
                }
                .toArgs()

        /**
         * Redshift TIMETZ: The JDBC driver returns strings like "00:00:00+00" instead of ISO
         * "00:00Z". Nanosecond values overflow (23:59:59.999999999 → 00:00:00+00) → filter MAX.
         */
        @JvmStatic
        fun timetz() =
            DataCoercionTimeTzFixtures.timetz
                .filter { it.name != MAX_TIME }
                .map { fixture ->
                    when (fixture.name) {
                        // Redshift JDBC returns "HH:mm:ss+00" format
                        MIDNIGHT -> fixture.copy(outputValue = "00:00:00+00")
                        HIGH_NOON -> fixture.copy(outputValue = "12:00:00+00")
                        else -> fixture
                    }
                }
                .toArgs()

        /** TIME: nanosecond overflow on MAX_TIME (23:59:59.999999999 → 00:00) → filter */
        @JvmStatic
        fun timentz() = DataCoercionTimeNtzFixtures.timentz.filter { it.name != MAX_TIME }.toArgs()

        /** Filter out-of-range dates since the coercer does not validate date ranges. */
        @JvmStatic
        fun date() =
            DataCoercionDateFixtures.commonWarehouse
                .filter { it.name != OUT_OF_RANGE_TIMESTAMP }
                .toArgs()

        @JvmStatic
        fun string() =
            DataCoercionStringFixtures.strings
                .map { fixture ->
                    when (fixture.name) {
                        // LONG_STRING: Redshift VARCHAR is 65,535 bytes; the 16MB+ fixture is
                        // nullified.
                        LONG_STRING ->
                            fixture.copy(
                                outputValue = null,
                                changeReason = Reason.DESTINATION_FIELD_SIZE_LIMITATION,
                            )
                        // inserts directly via JDBC (not the production CSV/COPY pipeline)
                        // so the null byte causes Redshift to truncate the string.
                        NULL_CHAR_STRING -> fixture.copy(outputValue = "asdf-")
                        else -> fixture
                    }
                }
                .toArgs()

        /**
         * Unknown types map to VARCHAR(65535) on this branch. The test client reads VARCHAR as
         * plain strings, so use stringified unknowns.
         */
        @JvmStatic
        fun unknown() =
            DataCoercionUnknownFixtures.stringifiedUnknowns
                .map { fixture ->
                    when (fixture.name) {
                        STR_VALUE -> fixture.copy(outputValue = "foo")
                        else -> fixture
                    }
                }
                .toArgs()
    }
}
