/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mysql

import io.airbyte.cdk.data.LocalDateCodec
import io.airbyte.cdk.data.LocalDateTimeCodec
import io.airbyte.cdk.data.LocalTimeCodec
import io.airbyte.cdk.data.OffsetDateTimeCodec
import io.airbyte.cdk.read.cdc.Converted
import io.airbyte.cdk.read.cdc.NoConversion
import io.airbyte.cdk.read.cdc.NullFallThrough
import io.airbyte.cdk.read.cdc.PartialConverter
import io.airbyte.cdk.read.cdc.RelationalColumnCustomConverter
import io.debezium.spi.converter.RelationalColumn
import java.time.Duration
import java.time.Instant
import java.time.LocalDate
import java.time.LocalDateTime
import java.time.LocalTime
import java.time.OffsetDateTime
import java.time.ZoneOffset
import java.time.ZonedDateTime
import java.time.temporal.ChronoUnit
import org.apache.kafka.connect.data.SchemaBuilder

class MySqlSourceCdcTemporalConverter : RelationalColumnCustomConverter {

    override val debeziumPropertiesKey: String = "temporal"

    override val handlers: List<RelationalColumnCustomConverter.Handler> =
        listOf(
            DatetimeMillisHandler,
            DatetimeMicrosHandler,
            DateHandler,
            TimeHandler,
            TimestampHandler
        )

    /**
     * MySQL permits zero-values (e.g. 0000-00-00 00:00:00) for DATE, DATETIME, and TIMESTAMP. These
     * aren't valid dates. For this reason, Debezium injects zeroDateTimeBehavior=CONVERT_TO_NULL in the JDBC param
     * which will convert zero dates (i.e. 0000-00-00 00:00:00) to NULL (ref
     * https://github.com/debezium/debezium/blob/f13c18f0db7bb5be47c8c4b427e7138da2a29d99/debezium-connector-mysql/src/main/java/io/debezium/connector/mysql/jdbc/MySqlConnectionConfiguration.java#L23).
     *
     * When a zero date is converted to NULL for a non-nullable column, Kafka throws
     * `Invalid value: null used for required field` and terminates the sync. To handle this, we added optional() in
     * DATE and DATETIME (micro and millis) so that zero-date that converts to NULL no longer violates a required field.
     *
     * Here is the mapping:
     * - Datetime (micro and millis): invalid, interpreted as NULL
     * - Date: invalid, interpreted as NULL
     * - Timestamp: interpreted as 0, which is then converted to the Unix epoch, 1970-01-01. Snapshot reads can still
     * produce NULL values.
     * - Time: 00:00:00 represents midnight, which is a valid time value.
     */
    data object DatetimeMillisHandler : RelationalColumnCustomConverter.Handler {

        override fun matches(column: RelationalColumn): Boolean =
            column.typeName().equals("DATETIME", ignoreCase = true) &&
                column.length().orElse(0) <= 3

        // Zero date `datetime(3)` is converted to NULL, optional() lets a NOT NULL column emit NULL
        override fun outputSchemaBuilder(): SchemaBuilder = SchemaBuilder.string().optional()

        override val partialConverters: List<PartialConverter> =
            listOf(
                NullFallThrough,
                PartialConverter {
                    if (it is LocalDateTime) {
                        Converted(it.format(LocalDateTimeCodec.formatter))
                    } else {
                        NoConversion
                    }
                },
                PartialConverter {
                    // Required for default values.
                    if (it is Number) {
                        val delta: Duration = Duration.ofMillis(it.toLong())
                        val instant: Instant = Instant.EPOCH.plus(delta)
                        val localDateTime: LocalDateTime =
                            LocalDateTime.ofInstant(instant, ZoneOffset.UTC)
                        Converted(localDateTime.format(LocalDateTimeCodec.formatter))
                    } else {
                        NoConversion
                    }
                }
            )
    }

    data object DatetimeMicrosHandler : RelationalColumnCustomConverter.Handler {

        override fun matches(column: RelationalColumn): Boolean =
            column.typeName().equals("DATETIME", ignoreCase = true) && column.length().orElse(0) > 3

        // Zero date `datetime(6)` is converted to NULL, optional() lets a NOT NULL column emit NULL
        override fun outputSchemaBuilder(): SchemaBuilder = SchemaBuilder.string().optional()

        override val partialConverters: List<PartialConverter> =
            listOf(
                NullFallThrough,
                PartialConverter {
                    if (it is LocalDateTime) {
                        Converted(it.format(LocalDateTimeCodec.formatter))
                    } else {
                        NoConversion
                    }
                },
                PartialConverter {
                    // Required for default values.
                    if (it is Number) {
                        val delta: Duration = Duration.of(it.toLong(), ChronoUnit.MICROS)
                        val instant: Instant = Instant.EPOCH.plus(delta)
                        val localDateTime: LocalDateTime =
                            LocalDateTime.ofInstant(instant, ZoneOffset.UTC)
                        Converted(localDateTime.format(LocalDateTimeCodec.formatter))
                    } else {
                        NoConversion
                    }
                }
            )
    }

    data object DateHandler : RelationalColumnCustomConverter.Handler {

        override fun matches(column: RelationalColumn): Boolean =
            column.typeName().equals("DATE", ignoreCase = true)

        // Zero date `date` is converted to NULL, optional() lets a NOT NULL column emit NULL
        override fun outputSchemaBuilder(): SchemaBuilder = SchemaBuilder.string().optional()

        override val partialConverters: List<PartialConverter> =
            listOf(
                NullFallThrough,
                PartialConverter {
                    if (it is LocalDate) {
                        Converted(it.format(LocalDateCodec.formatter))
                    } else {
                        NoConversion
                    }
                },
                PartialConverter {
                    // Required for default values.
                    if (it is Number) {
                        val localDate: LocalDate = LocalDate.ofEpochDay(it.toLong())
                        Converted(localDate.format(LocalDateCodec.formatter))
                    } else {
                        NoConversion
                    }
                }
            )
    }

    data object TimeHandler : RelationalColumnCustomConverter.Handler {

        override fun matches(column: RelationalColumn): Boolean =
            column.typeName().equals("TIME", ignoreCase = true)

        override fun outputSchemaBuilder(): SchemaBuilder = SchemaBuilder.string()

        override val partialConverters: List<PartialConverter> =
            listOf(
                NullFallThrough,
                PartialConverter {
                    if (it is Duration) {
                        val localTime: LocalTime = LocalTime.MIDNIGHT.plus(it)
                        Converted(localTime.format(LocalTimeCodec.formatter))
                    } else {
                        NoConversion
                    }
                },
                PartialConverter {
                    // Required for default values.
                    if (it is Number) {
                        val delta: Duration = Duration.of(it.toLong(), ChronoUnit.MICROS)
                        val localTime: LocalTime = LocalTime.ofNanoOfDay(delta.toNanos())
                        Converted(localTime.format(LocalTimeCodec.formatter))
                    } else {
                        NoConversion
                    }
                }
            )
    }

    data object TimestampHandler : RelationalColumnCustomConverter.Handler {
        override fun matches(column: RelationalColumn): Boolean =
            column.typeName().equals("TIMESTAMP", ignoreCase = true)

        override fun outputSchemaBuilder(): SchemaBuilder = SchemaBuilder.string()

        override val partialConverters: List<PartialConverter> =
            listOf(
                NullFallThrough,
                PartialConverter {
                    if (it is ZonedDateTime) {
                        val offsetDateTime: OffsetDateTime = it.toOffsetDateTime()
                        Converted(offsetDateTime.format(OffsetDateTimeCodec.formatter))
                    } else {
                        NoConversion
                    }
                },
                PartialConverter {
                    // Required for default values.
                    if (it is String) {
                        val instant: Instant = Instant.parse(it)
                        val offsetDateTime: OffsetDateTime =
                            OffsetDateTime.ofInstant(instant, ZoneOffset.UTC)
                        Converted(offsetDateTime.format(OffsetDateTimeCodec.formatter))
                    } else {
                        NoConversion
                    }
                }
            )
    }
}
