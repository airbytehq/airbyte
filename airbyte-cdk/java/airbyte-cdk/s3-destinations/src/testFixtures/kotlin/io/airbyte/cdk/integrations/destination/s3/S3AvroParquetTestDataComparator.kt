/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.destination.s3

import io.airbyte.cdk.integrations.standardtest.destination.comparator.AdvancedTestDataComparator
import java.time.*
import java.time.format.DateTimeFormatter

class S3AvroParquetTestDataComparator : AdvancedTestDataComparator() {
    override fun compareDateValues(airbyteMessageValue: String, destinationValue: String): Boolean {
        val destinationDate = LocalDate.ofEpochDay(destinationValue.toLong())
        val expectedDate =
            LocalDate.parse(
                airbyteMessageValue,
                DateTimeFormatter.ofPattern(AdvancedTestDataComparator.AIRBYTE_DATE_FORMAT)
            )
        return expectedDate == destinationDate
    }

    private fun getInstantFromEpoch(epochValue: String): Instant {
        return Instant.ofEpochMilli(epochValue.toLong() / 1000)
    }

    override fun parseDestinationDateWithTz(destinationValue: String): ZonedDateTime {
        return ZonedDateTime.ofInstant(getInstantFromEpoch(destinationValue), ZoneOffset.UTC)
    }

    override fun compareDateTimeValues(
        airbyteMessageValue: String,
        destinationValue: String
    ): Boolean {
        val format = DateTimeFormatter.ofPattern(AdvancedTestDataComparator.AIRBYTE_DATETIME_FORMAT)
        val dateTime =
            LocalDateTime.ofInstant(getInstantFromEpoch(destinationValue), ZoneOffset.UTC)
        return super.compareDateTimeValues(airbyteMessageValue, format.format(dateTime))
    }
}
