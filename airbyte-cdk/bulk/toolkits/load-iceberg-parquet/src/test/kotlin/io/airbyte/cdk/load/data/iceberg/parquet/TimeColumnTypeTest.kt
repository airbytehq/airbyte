/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.load.data.iceberg.parquet

import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.load.command.iceberg.parquet.TimeColumnType
import io.airbyte.cdk.load.data.ArrayType
import io.airbyte.cdk.load.data.FieldType
import io.airbyte.cdk.load.data.NullValue
import io.airbyte.cdk.load.data.ObjectType
import io.airbyte.cdk.load.data.TimeTypeWithTimezone
import io.airbyte.cdk.load.data.TimeTypeWithoutTimezone
import io.airbyte.cdk.load.data.TimeWithTimezoneValue
import io.airbyte.cdk.load.data.TimeWithoutTimezoneValue
import io.airbyte.cdk.load.toolkits.iceberg.parquet.IcebergSuperTypeFinder
import io.airbyte.cdk.load.toolkits.iceberg.parquet.IcebergTypesComparator
import java.time.LocalTime
import java.time.OffsetTime
import java.time.ZoneOffset
import org.apache.iceberg.types.Types
import org.assertj.core.api.Assertions.assertThat
import org.assertj.core.api.Assertions.assertThatThrownBy
import org.junit.jupiter.api.Test

class TimeColumnTypeTest {
    @Test
    fun `time schemas default to TIME and optionally become strings including array elements`() {
        for (type in listOf(TimeTypeWithTimezone, TimeTypeWithoutTimezone)) {
            assertThat(AirbyteTypeToIcebergSchema().convert(type, false))
                .isEqualTo(Types.TimeType.get())
            val converter = AirbyteTypeToIcebergSchema(TimeColumnType.STRING)
            assertThat(converter.convert(type, false)).isEqualTo(Types.StringType.get())
            assertThat(
                    converter
                        .convert(ArrayType(FieldType(type, true)), false)
                        .asListType()
                        .elementType(),
                )
                .isEqualTo(Types.StringType.get())
            assertThat(
                    ObjectType(linkedMapOf("time" to FieldType(type, true)))
                        .toIcebergSchema(emptyList(), TimeColumnType.STRING)
                        .findType("time"),
                )
                .isEqualTo(Types.StringType.get())
        }
        assertThat(
                ObjectType(linkedMapOf())
                    .toIcebergSchema(emptyList(), TimeColumnType.STRING)
                    .columns(),
            )
            .isEmpty()
    }

    @Test
    fun `string time values preserve local time precision and offset`() {
        val converter = AirbyteValueToIcebergRecord()
        for (text in listOf("00:00", "12:34:56.123456", "23:59:59.999999999")) {
            val time = LocalTime.parse(text)
            assertThat(converter.convert(TimeWithoutTimezoneValue(time), Types.StringType.get()))
                .isEqualTo(time.toString())
            assertThat(converter.convert(TimeWithoutTimezoneValue(time), Types.TimeType.get()))
                .isEqualTo(time)
        }
        for (text in listOf("12:34:56.123456+05:30", "00:00-07:00", "23:59Z")) {
            val time = OffsetTime.parse(text)
            assertThat(converter.convert(TimeWithTimezoneValue(time), Types.StringType.get()))
                .isEqualTo(time.toString())
            assertThat(converter.convert(TimeWithTimezoneValue(time), Types.TimeType.get()))
                .isEqualTo(time.withOffsetSameInstant(ZoneOffset.UTC).toLocalTime())
        }
        assertThat(converter.convert(NullValue, Types.StringType.get())).isNull()
        assertThatThrownBy {
                converter.convert(TimeWithoutTimezoneValue(LocalTime.NOON), Types.LongType.get())
            }
            .isInstanceOf(IllegalArgumentException::class.java)
    }

    @Test
    fun `existing time columns cannot be promoted to string`() {
        val finder = IcebergSuperTypeFinder(IcebergTypesComparator())
        assertThatThrownBy {
                finder.findSuperType(Types.TimeType.get(), Types.StringType.get(), "time")
            }
            .isInstanceOf(ConfigErrorException::class.java)
            .hasMessageContaining("full refresh")
            .hasMessageContaining("time_column_type")
    }
}
