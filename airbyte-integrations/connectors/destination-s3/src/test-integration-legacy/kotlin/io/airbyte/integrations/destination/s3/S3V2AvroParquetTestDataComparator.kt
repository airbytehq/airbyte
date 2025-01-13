/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.s3

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.integrations.standardtest.destination.comparator.AdvancedTestDataComparator
import java.nio.charset.StandardCharsets
import java.time.*
import java.time.format.DateTimeFormatter
import java.util.*

class S3V2AvroParquetTestDataComparator : AdvancedTestDataComparator() {
    override fun compareDateValues(airbyteMessageValue: String, destinationValue: String): Boolean {
        val destinationDate = LocalDate.ofEpochDay(destinationValue.toLong())
        val expectedDate = LocalDate.parse(airbyteMessageValue, DateTimeFormatter.ISO_LOCAL_DATE)
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
        val destinationDate =
            LocalDateTime.ofInstant(getInstantFromEpoch(destinationValue), ZoneOffset.UTC)
        return super.compareDateTimeValues(airbyteMessageValue, destinationDate.toString())
    }

    override fun compareTimeWithoutTimeZone(
        airbyteMessageValue: String,
        destinationValue: String
    ): Boolean {
        val destinationDate =
            LocalTime.ofInstant(getInstantFromEpoch(destinationValue), ZoneOffset.UTC)
        val expectedDate = LocalTime.parse(airbyteMessageValue, DateTimeFormatter.ISO_TIME)
        return expectedDate == destinationDate
    }

    override fun compareString(expectedValue: JsonNode, actualValue: JsonNode): Boolean {
        // to handle base64 encoded strings
        return expectedValue.asText() == actualValue.asText() ||
            decodeBase64(expectedValue.asText()) == actualValue.asText()
    }

    private fun decodeBase64(string: String): String {
        val decoded = Base64.getDecoder().decode(string)
        return String(decoded, StandardCharsets.UTF_8)
    }
}
