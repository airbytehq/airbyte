/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.data

import io.airbyte.cdk.load.message.DestinationRecord
import io.airbyte.cdk.load.test.util.Root
import io.airbyte.cdk.load.test.util.SchemaRecordBuilder
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

class TimeStringToIntegerTest {

    @Test
    fun testMapDate() {
        val mapper = TimeStringToInteger(DestinationRecord.Meta())
        listOf(
                "2021-1-1" to 18628,
                "2021-01-01" to 18628,
                "2021/01/02" to 18629,
                "2021.01.03" to 18630,
                "2021 Jan 04" to 18631,
                "2021-1-1 BC" to -1457318
            )
            .forEach {
                Assertions.assertEquals(
                    IntValue(it.second),
                    mapper.mapDate(DateValue(it.first), emptyList()),
                    "Failed for ${it.first} to ${it.second}"
                )
            }
    }

    private val timestampPairs =
        listOf(
            "2018-09-15 12:00:00" to 1537012800000000,
            "2018-09-15 12:00:00.006542" to 1537012800006542,
            "2018/09/15 12:00:00" to 1537012800000000,
            "2018.09.15 12:00:00" to 1537012800000000,
            "2018 Jul 15 12:00:00" to 1531656000000000,
            "2018 Jul 15 12:00:00 GMT+08:00" to 1531627200000000,
            "2018 Jul 15 12:00:00GMT+07" to 1531630800000000,
            "2021-1-1 01:01:01" to 1609462861000000,
            "2021.1.1 01:01:01" to 1609462861000000,
            "2021/1/1 01:01:01" to 1609462861000000,
            "2021-1-1 01:01:01 +01" to 1609459261000000,
            "2021-01-01T01:01:01+01:00" to 1609459261000000,
            "2021-01-01T01:01:01.546+01:00" to 1609459261546000,
            "2021-01-01 01:01:01" to 1609462861000000,
            "2021-01-01 01:01:01 +0000" to 1609462861000000,
            "2021/01/01 01:01:01 +0000" to 1609462861000000,
            "2021-01-01T01:01:01Z" to 1609462861000000,
            "2021-01-01T01:01:01-01:00" to 1609466461000000,
            "2021-01-01T01:01:01+01:00" to 1609459261000000,
            "2021-01-01 01:01:01 UTC" to 1609462861000000,
            "2021-01-01T01:01:01 PST" to 1609491661000000,
            "2021-01-01T01:01:01 +0000" to 1609462861000000,
            "2021-01-01T01:01:01+0000" to 1609462861000000,
            "2021-01-01T01:01:01UTC" to 1609462861000000,
            "2021-01-01T01:01:01+01" to 1609459261000000,
            "2022-01-23T01:23:45.678-11:30 BC" to -125941863974322000,
            "2022-01-23T01:23:45.678-11:30" to 1642942425678000
        )

    @Test
    fun testMapTimestampWithTimezone() {
        val mapper = TimeStringToInteger(DestinationRecord.Meta())
        timestampPairs.forEach {
            Assertions.assertEquals(
                IntegerValue(it.second),
                mapper.mapTimestampWithTimezone(TimestampValue(it.first), emptyList()),
                "Failed for ${it.first} to ${it.second}"
            )
        }
    }

    @Test
    fun testMapTimestampWithoutTimezone() {
        val mapper = TimeStringToInteger(DestinationRecord.Meta())
        timestampPairs.forEach {
            Assertions.assertEquals(
                IntegerValue(it.second),
                mapper.mapTimestampWithoutTimezone(TimestampValue(it.first), emptyList()),
                "Failed for ${it.first} to ${it.second}"
            )
        }
    }

    private val timePairs =
        listOf(
            "01:01:01" to 3661000000,
            "01:01" to 3660000000,
            "12:23:01.541" to 44581541000,
            "12:23:01.541214" to 44581541214,
            "12:00:00.000000+01:00" to 39600000000,
            "10:00:00.000000-01:00" to 39600000000,
            "03:30:00.000000+04:00" to 84600000000
        )

    @Test
    fun testTimeWithTimezone() {
        val mapper = TimeStringToInteger(DestinationRecord.Meta())
        timePairs.forEach {
            Assertions.assertEquals(
                IntegerValue(it.second),
                mapper.mapTimeWithTimezone(TimeValue(it.first), emptyList()),
                "Failed for ${it.first} to ${it.second}"
            )
        }
    }

    @Test
    fun testTimeWithoutTimezone() {
        val mapper = TimeStringToInteger(DestinationRecord.Meta())
        timePairs.forEach {
            Assertions.assertEquals(
                IntegerValue(it.second),
                mapper.mapTimeWithoutTimezone(TimeValue(it.first), emptyList()),
                "Failed for ${it.first} to ${it.second}"
            )
        }
    }

    @Test
    fun testBasicSchemaBehavior() {
        val (inputSchema, expectedOutput) =
            SchemaRecordBuilder<Root>()
                .with(DateType, IntegerType)
                .withRecord()
                .with(TimestampTypeWithTimezone, IntegerType)
                .endRecord()
                .with(TimestampTypeWithoutTimezone, IntegerType)
                .withRecord()
                .with(TimeTypeWithTimezone, IntegerType)
                .withRecord()
                .with(TimeTypeWithoutTimezone, IntegerType)
                .endRecord()
                .endRecord()
                .withUnion(
                    expectedInstead =
                        FieldType(UnionType(listOf(IntegerType, IntegerType)), nullable = false)
                )
                .with(DateType)
                .with(TimeTypeWithTimezone)
                .endUnion()
                .build()
        val output = TimeStringTypeToIntegerType().map(inputSchema)
        Assertions.assertEquals(expectedOutput, output)
    }
}
