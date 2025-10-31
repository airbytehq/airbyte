/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
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
import io.github.oshai.kotlinlogging.KotlinLogging
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
            DatetimeMillisHandler(),
            DatetimeMicrosHandler(),
            DateHandler(),
            TimeHandler, // zero-dates are valid, conversion is not needed
            TimestampHandler // zero-dates are being converted to epoch
        )

    companion object {
        private val log = KotlinLogging.logger {}

        // Logs column information.
        fun logColumnNullHandling(
            handlerName: String,
            column: RelationalColumn?,
        ) {
            if (column != null) {
                // Log detailed column metadata
                log.info {
                    "$handlerName - column info: ${column.name()}, " +
                        "isNullable=${column.isOptional}, " +
                        "hasDefaultValue=${column.hasDefaultValue()}, " +
                        "defaultValue=${column.defaultValue()}, " +
                        "jdbcType=${column.jdbcType()}, " +
                        "typeName=${column.typeName()}, " +
                        "typeExpression=${column.typeExpression()}"
                }
            }
        }
    }

    /**
     * Handles MySQL zero-dates (e.g., '0000-00-00 00:00:00'), which are not valid temporal types in
     * Java. MySQL/JDBC behavior for zero-dates:
     * - DATETIME and DATE columns: Zero-dates are converted to NULL
     * - TIMESTAMP columns: Zero-dates are represented as 0 on the binlog.
     * - TIME columns: '00:00:00' is a valid value and NOT considered a zero-date
     *
     * Non-null DEFAULT values that are zero-dates are converted to Unix epoch.
     *
     * Debezium throws a schema validation error when it receives NULL for a non-nullable column:
     * https://github.com/debezium/debezium/blob/db880a1969b6dc90bbc6691051d06abdb8a73cb5/debezium-core/src/main/java/io/debezium/relational/TableSchemaBuilder.java#L344
     * Our conversion strategy:
     * - Nullable columns: NULL passes through unchanged
     * - Non-nullable columns: NULL (from zero-dates) → epoch (1970-01-01) to prevent Debezium
     * errors
     *
     * Note: This handler is only needed for DATETIME and DATE types. TIME values don't have a
     * zero-date issue since '00:00:00' is a valid time (midnight). TIMESTAMP zero-dates
     * ('0000-00-00 00:00:00') are stored as 0 internally in the binlog, which gets interpreted as
     * the Unix epoch (1970-01-01 00:00:00 UTC).
     */
    class DatetimeMillisHandler : RelationalColumnCustomConverter.Handler {
        private var currentColumn: RelationalColumn? = null

        override fun matches(column: RelationalColumn): Boolean {
            this.currentColumn = column
            val matches =
                column.typeName().equals("DATETIME", ignoreCase = true) &&
                    column.length().orElse(0) <= 3
            return matches
        }

        override fun outputSchemaBuilder(): SchemaBuilder = SchemaBuilder.string()

        override val partialConverters: List<PartialConverter>
            get() {
                val columnRefForConverters = currentColumn
                logColumnNullHandling("DatetimeMillisHandler", columnRefForConverters)
                return listOf(
                    PartialConverter {
                        if (it == null) {
                            if (columnRefForConverters?.isOptional == true) {
                                Converted(null)
                            } else {
                                val epoch = LocalDateTime.ofInstant(Instant.EPOCH, ZoneOffset.UTC)
                                Converted(epoch.format(LocalDateTimeCodec.formatter))
                            }
                        } else {
                            NoConversion
                        }
                    },
                    PartialConverter {
                        if (it is LocalDateTime) {
                            Converted(it.format(LocalDateTimeCodec.formatter))
                        } else {
                            NoConversion
                        }
                    },
                    PartialConverter {
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
    }

    class DatetimeMicrosHandler : RelationalColumnCustomConverter.Handler {
        private var currentColumn: RelationalColumn? = null

        override fun matches(column: RelationalColumn): Boolean {
            this.currentColumn = column
            val matches =
                column.typeName().equals("DATETIME", ignoreCase = true) &&
                    column.length().orElse(0) > 3
            return matches
        }

        override fun outputSchemaBuilder(): SchemaBuilder = SchemaBuilder.string()

        override val partialConverters: List<PartialConverter>
            get() {
                val columnRefForConverters = currentColumn
                logColumnNullHandling("DatetimeMicrosHandler", columnRefForConverters)
                return listOf(
                    PartialConverter {
                        if (it == null) {
                            if (columnRefForConverters?.isOptional == true) {
                                Converted(null)
                            } else {
                                val epoch = LocalDateTime.ofInstant(Instant.EPOCH, ZoneOffset.UTC)
                                Converted(epoch.format(LocalDateTimeCodec.formatter))
                            }
                        } else {
                            NoConversion
                        }
                    },
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
    }

    class DateHandler : RelationalColumnCustomConverter.Handler {
        private var currentColumn: RelationalColumn? = null

        override fun matches(column: RelationalColumn): Boolean {
            this.currentColumn = column
            val matches = column.typeName().equals("DATE", ignoreCase = true)
            return matches
        }

        override fun outputSchemaBuilder(): SchemaBuilder = SchemaBuilder.string()

        override val partialConverters: List<PartialConverter>
            get() {
                val columnRefForConverters = currentColumn
                logColumnNullHandling("DateHandler", columnRefForConverters)
                return listOf(
                    PartialConverter {
                        if (it == null) {
                            if (columnRefForConverters?.isOptional == true) {
                                Converted(null)
                            } else {
                                val epoch = LocalDate.ofEpochDay(0)
                                Converted(epoch.format(LocalDateCodec.formatter))
                            }
                        } else {
                            NoConversion
                        }
                    },
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
    }
    /**
     * TIME supports '00:00:00' and it is considered valid, see
     * https://dev.mysql.com/doc/refman/8.0/en/time.html. If we get a null value from the server, it
     * means the TIME is invalid/corrupt and in that case we should return null.
     */
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

    /**
     * TIMESTAMP zero dates '0000-00-00 00:00:00' are stored as a zero (integer) internally and is
     * interpreted as epoch (1970-01-01 00:00:00 UTC). See
     * https://dev.mysql.com/doc/refman/8.4/en/date-and-time-type-syntax.html#:~:text=A%20timestamp.%20The,%E2%80%9D%20TIMESTAMP%20value.
     */
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
