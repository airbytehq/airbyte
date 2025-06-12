/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.data

import java.time.LocalDate
import java.time.LocalDateTime
import java.time.OffsetDateTime
import java.time.ZoneOffset
import java.time.format.DateTimeParseException
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertThrows
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.assertAll

class AirbyteValueCoercerTest {

    @Test
    fun testDateTimeFormatterBasicDates() {
        assertAll(
            {
                assertEquals(
                    LocalDate.of(2024, 1, 15),
                    LocalDate.parse("2024-01-15", AirbyteValueCoercer.DATE_TIME_FORMATTER)
                )
            },
            {
                assertEquals(
                    LocalDate.of(1999, 12, 31),
                    LocalDate.parse("1999-12-31", AirbyteValueCoercer.DATE_TIME_FORMATTER)
                )
            },
            {
                assertEquals(
                    LocalDate.of(2025, 6, 15),
                    LocalDate.parse("2025-06-15", AirbyteValueCoercer.DATE_TIME_FORMATTER)
                )
            }
        )
    }

    @Test
    fun testDateTimeFormatterWith2DigitYears() {
        assertAll(
            // 2-digit years (will be interpreted as 20xx)
            {
                assertEquals(
                    LocalDate.of(24, 1, 15),
                    LocalDate.parse("24-01-15", AirbyteValueCoercer.DATE_TIME_FORMATTER)
                )
            },
            {
                assertEquals(
                    LocalDate.of(99, 12, 31),
                    LocalDate.parse("99-12-31", AirbyteValueCoercer.DATE_TIME_FORMATTER)
                )
            },
            {
                assertEquals(
                    LocalDate.of(1, 6, 15),
                    LocalDate.parse("01-06-15", AirbyteValueCoercer.DATE_TIME_FORMATTER)
                )
            }
        )
    }

    @Test
    fun testDateTimeFormatterWithAlternateSeparators() {
        assertAll(
            // Slash separators
            {
                assertEquals(
                    LocalDate.of(2024, 1, 15),
                    LocalDate.parse("2024/01/15", AirbyteValueCoercer.DATE_TIME_FORMATTER)
                )
            },
            {
                assertEquals(
                    LocalDate.of(99, 12, 31),
                    LocalDate.parse("99/12/31", AirbyteValueCoercer.DATE_TIME_FORMATTER)
                )
            },
            {
                assertEquals(
                    LocalDate.of(12345, 6, 15),
                    LocalDate.parse("12345/06/15", AirbyteValueCoercer.DATE_TIME_FORMATTER)
                )
            },

            // Dot separators
            {
                assertEquals(
                    LocalDate.of(2024, 1, 15),
                    LocalDate.parse("2024.01.15", AirbyteValueCoercer.DATE_TIME_FORMATTER)
                )
            },
            {
                assertEquals(
                    LocalDate.of(99, 12, 31),
                    LocalDate.parse("99.12.31", AirbyteValueCoercer.DATE_TIME_FORMATTER)
                )
            },
            {
                assertEquals(
                    LocalDate.of(12345, 6, 15),
                    LocalDate.parse("12345.06.15", AirbyteValueCoercer.DATE_TIME_FORMATTER)
                )
            },

            // Space separators
            {
                assertEquals(
                    LocalDate.of(2024, 1, 15),
                    LocalDate.parse("2024 01 15", AirbyteValueCoercer.DATE_TIME_FORMATTER)
                )
            },
            {
                assertEquals(
                    LocalDate.of(99, 12, 31),
                    LocalDate.parse("99 12 31", AirbyteValueCoercer.DATE_TIME_FORMATTER)
                )
            },

            // Mixed separators (dashes, slashes, dots, spaces)
            {
                assertEquals(
                    LocalDate.of(2024, 1, 15),
                    LocalDate.parse("2024-01/15", AirbyteValueCoercer.DATE_TIME_FORMATTER)
                )
            },
            {
                assertEquals(
                    LocalDate.of(2024, 1, 15),
                    LocalDate.parse("2024/01-15", AirbyteValueCoercer.DATE_TIME_FORMATTER)
                )
            },
            {
                assertEquals(
                    LocalDate.of(2024, 1, 15),
                    LocalDate.parse("2024.01-15", AirbyteValueCoercer.DATE_TIME_FORMATTER)
                )
            },
            {
                assertEquals(
                    LocalDate.of(2024, 1, 15),
                    LocalDate.parse("2024 01/15", AirbyteValueCoercer.DATE_TIME_FORMATTER)
                )
            },

            // Separators with time and timezone
            {
                assertEquals(
                    LocalDateTime.of(2024, 1, 15, 14, 30, 45),
                    LocalDateTime.parse(
                        "2024/01/15T14:30:45",
                        AirbyteValueCoercer.DATE_TIME_FORMATTER
                    )
                )
            },
            {
                assertEquals(
                    LocalDateTime.of(2024, 1, 15, 14, 30, 45),
                    LocalDateTime.parse(
                        "2024.01.15T14:30:45",
                        AirbyteValueCoercer.DATE_TIME_FORMATTER
                    )
                )
            },
            {
                assertEquals(
                    OffsetDateTime.of(2024, 1, 15, 14, 30, 0, 0, ZoneOffset.UTC),
                    OffsetDateTime.parse(
                        "2024/01/15T14:30Z",
                        AirbyteValueCoercer.DATE_TIME_FORMATTER
                    )
                )
            }
        )
    }

    @Test
    fun testDateTimeFormatterWithNegativeYears() {
        assertAll(
            {
                assertEquals(
                    LocalDate.of(-1, 12, 31),
                    LocalDate.parse("-0001-12-31", AirbyteValueCoercer.DATE_TIME_FORMATTER)
                )
            },
            {
                assertEquals(
                    LocalDate.of(-1000, 6, 15),
                    LocalDate.parse("-1000-06-15", AirbyteValueCoercer.DATE_TIME_FORMATTER)
                )
            },
            {
                assertEquals(
                    LocalDate.of(-4567, 3, 20),
                    LocalDate.parse("-4567-03-20", AirbyteValueCoercer.DATE_TIME_FORMATTER)
                )
            }
        )
    }

    @Test
    fun testDateTimeFormatterWithLargeYears() {
        assertAll(
            // Test large positive years (tens of thousands)
            {
                assertEquals(
                    LocalDate.of(12345, 1, 1),
                    LocalDate.parse("12345-01-01", AirbyteValueCoercer.DATE_TIME_FORMATTER)
                )
            },
            {
                assertEquals(
                    LocalDate.of(99999, 12, 31),
                    LocalDate.parse("99999-12-31", AirbyteValueCoercer.DATE_TIME_FORMATTER)
                )
            },
            {
                assertEquals(
                    LocalDate.of(-12345, 6, 15),
                    LocalDate.parse("-12345-06-15", AirbyteValueCoercer.DATE_TIME_FORMATTER)
                )
            },
            {
                assertEquals(
                    LocalDate.of(-99999, 3, 10),
                    LocalDate.parse("-99999-03-10", AirbyteValueCoercer.DATE_TIME_FORMATTER)
                )
            }
        )
    }

    @Test
    fun testDateTimeFormatterWithTimezones() {
        assertAll(
            // UTC timezone
            {
                assertEquals(
                    OffsetDateTime.of(2024, 1, 15, 14, 30, 0, 0, ZoneOffset.UTC),
                    OffsetDateTime.parse(
                        "2024-01-15T14:30Z",
                        AirbyteValueCoercer.DATE_TIME_FORMATTER
                    )
                )
            },

            // ISO offset format with colon
            {
                assertEquals(
                    OffsetDateTime.of(2024, 1, 15, 14, 30, 0, 0, ZoneOffset.ofHours(5)),
                    OffsetDateTime.parse(
                        "2024-01-15T14:30+05:00",
                        AirbyteValueCoercer.DATE_TIME_FORMATTER
                    )
                )
            },
            {
                assertEquals(
                    OffsetDateTime.of(2024, 1, 15, 14, 30, 0, 0, ZoneOffset.ofHours(-8)),
                    OffsetDateTime.parse(
                        "2024-01-15T14:30-08:00",
                        AirbyteValueCoercer.DATE_TIME_FORMATTER
                    )
                )
            },

            // ISO offset format without colon
            {
                assertEquals(
                    OffsetDateTime.of(2024, 1, 15, 14, 30, 0, 0, ZoneOffset.ofHours(3)),
                    OffsetDateTime.parse(
                        "2024-01-15T14:30+03",
                        AirbyteValueCoercer.DATE_TIME_FORMATTER
                    )
                )
            },
            {
                assertEquals(
                    OffsetDateTime.of(2024, 1, 15, 14, 30, 0, 0, ZoneOffset.ofHours(-5)),
                    OffsetDateTime.parse(
                        "2024-01-15T14:30-05",
                        AirbyteValueCoercer.DATE_TIME_FORMATTER
                    )
                )
            }
        )
    }

    @Test
    fun testDateTimeFormatterWithoutTimezones() {
        assertAll(
            // Basic date
            {
                assertEquals(
                    LocalDate.of(2024, 1, 15),
                    LocalDate.parse("2024-01-15", AirbyteValueCoercer.DATE_TIME_FORMATTER)
                )
            },

            // Date with time but no timezone
            {
                assertEquals(
                    LocalDateTime.of(2024, 1, 15, 14, 30, 0),
                    LocalDateTime.parse("2024-01-15T14:30", AirbyteValueCoercer.DATE_TIME_FORMATTER)
                )
            },
            {
                assertEquals(
                    LocalDateTime.of(2024, 1, 15, 14, 30, 45),
                    LocalDateTime.parse(
                        "2024-01-15T14:30:45",
                        AirbyteValueCoercer.DATE_TIME_FORMATTER
                    )
                )
            },

            // Date with time and nanoseconds but no timezone
            {
                assertEquals(
                    LocalDateTime.of(2024, 1, 15, 14, 30, 45, 123456789),
                    LocalDateTime.parse(
                        "2024-01-15T14:30:45.123456789",
                        AirbyteValueCoercer.DATE_TIME_FORMATTER
                    )
                )
            }
        )
    }

    @Test
    fun testDateTimeFormatterCoercionWithDates() {
        assertAll(
            // Test coercion through coerceDate method
            {
                assertEquals(
                    DateValue(LocalDate.of(2024, 1, 15)),
                    AirbyteValueCoercer.coerceDate(StringValue("2024-01-15"))
                )
            },
            {
                assertEquals(
                    DateValue(LocalDate.of(-1000, 6, 15)),
                    AirbyteValueCoercer.coerceDate(StringValue("-1000-06-15"))
                )
            },
            {
                assertEquals(
                    DateValue(LocalDate.of(12345, 12, 31)),
                    AirbyteValueCoercer.coerceDate(StringValue("12345-12-31"))
                )
            }
        )
    }

    @Test
    fun testDateTimeFormatterExtremeCases() {
        assertAll(
            // Test very large years with our updated formatter
            {
                assertEquals(
                    LocalDate.of(999999, 1, 1),
                    LocalDate.parse("999999-01-01", AirbyteValueCoercer.DATE_TIME_FORMATTER)
                )
            },
            {
                assertEquals(
                    LocalDate.of(-999999, 12, 31),
                    LocalDate.parse("-999999-12-31", AirbyteValueCoercer.DATE_TIME_FORMATTER)
                )
            },

            // Test large years with timestamps
            {
                assertEquals(
                    LocalDateTime.of(123456, 6, 15, 12, 30, 45),
                    LocalDateTime.parse(
                        "123456-06-15T12:30:45",
                        AirbyteValueCoercer.DATE_TIME_FORMATTER
                    )
                )
            },
            {
                assertEquals(
                    LocalDateTime.of(-123456, 3, 20, 8, 15, 30, 123456789),
                    LocalDateTime.parse(
                        "-123456-03-20T08:15:30.123456789",
                        AirbyteValueCoercer.DATE_TIME_FORMATTER
                    )
                )
            }
        )
    }

    @Test
    fun testInvalidDateFormats() {
        assertAll(
            // Test that invalid formats throw exceptions
            {
                assertThrows(DateTimeParseException::class.java) {
                    LocalDate.parse("invalid-date", AirbyteValueCoercer.DATE_TIME_FORMATTER)
                }
            },
            {
                assertThrows(DateTimeParseException::class.java) {
                    LocalDate.parse(
                        "2024-13-01",
                        AirbyteValueCoercer.DATE_TIME_FORMATTER
                    ) // Invalid month
                }
            },
            {
                assertThrows(DateTimeParseException::class.java) {
                    LocalDate.parse(
                        "2024_01_15",
                        AirbyteValueCoercer.DATE_TIME_FORMATTER
                    ) // Underscores not supported
                }
            }
        )
    }
}
