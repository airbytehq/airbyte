/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.bigquery

import com.fasterxml.jackson.databind.JsonNode
import edu.umd.cs.findbugs.annotations.SuppressFBWarnings
import io.airbyte.cdk.integrations.destination.StandardNameTransformer
import io.airbyte.cdk.integrations.standardtest.destination.comparator.AdvancedTestDataComparator
import io.airbyte.commons.json.Jsons.deserialize
import java.time.LocalDate
import java.time.LocalDateTime
import java.time.ZoneOffset
import java.time.ZonedDateTime
import java.time.format.DateTimeFormatter
import org.slf4j.Logger
import org.slf4j.LoggerFactory

class BigQueryTestDataComparator : AdvancedTestDataComparator() {
    private val namingResolver = StandardNameTransformer()

    @SuppressFBWarnings("NP_PARAMETER_MUST_BE_NONNULL_BUT_MARKED_AS_NULLABLE")
    override fun resolveIdentifier(identifier: String?): List<String?> {
        val result: MutableList<String?> = ArrayList()
        result.add(identifier)
        result.add(namingResolver.getIdentifier(identifier!!))
        return result
    }

    private fun parseDate(dateValue: String?): LocalDate? {
        if (dateValue != null) {
            val format =
                (if (dateValue.matches(".+Z".toRegex())) BIGQUERY_DATETIME_FORMAT
                else AIRBYTE_DATE_FORMAT)
            return LocalDate.parse(dateValue, DateTimeFormatter.ofPattern(format))
        } else {
            return null
        }
    }

    private fun parseDateTime(dateTimeValue: String?): LocalDateTime? {
        if (dateTimeValue != null) {
            val format =
                (if (dateTimeValue.matches(".+Z".toRegex())) BIGQUERY_DATETIME_FORMAT
                else AIRBYTE_DATETIME_FORMAT)
            return LocalDateTime.parse(dateTimeValue, DateTimeFormatter.ofPattern(format))
        } else {
            return null
        }
    }

    override fun parseDestinationDateWithTz(destinationValue: String): ZonedDateTime {
        return if (destinationValue.matches(".+Z".toRegex())) {
            ZonedDateTime.of(
                LocalDateTime.parse(
                    destinationValue,
                    DateTimeFormatter.ofPattern(BIGQUERY_DATETIME_FORMAT)
                ),
                ZoneOffset.UTC
            )
        } else {
            ZonedDateTime.parse(destinationValue, airbyteDateTimeWithTzFormatter)
                .withZoneSameInstant(ZoneOffset.UTC)
        }
    }

    override fun compareDateTimeValues(expectedValue: String, actualValue: String): Boolean {
        val destinationDate = parseDateTime(actualValue)
        val expectedDate =
            LocalDateTime.parse(expectedValue, DateTimeFormatter.ofPattern(AIRBYTE_DATETIME_FORMAT))
        // #13123 Normalization issue
        if (expectedDate.isBefore(brokenDate.toLocalDateTime())) {
            LOGGER.warn(
                "Validation is skipped due to known Normalization issue. Values older then 1583 year and with time zone stored wrongly(lose days)."
            )
            return true
        } else {
            return expectedDate == destinationDate
        }
    }

    override fun compareDateValues(expectedValue: String, actualValue: String): Boolean {
        val destinationDate = parseDate(actualValue)
        val expectedDate =
            LocalDate.parse(expectedValue, DateTimeFormatter.ofPattern(AIRBYTE_DATE_FORMAT))
        return expectedDate == destinationDate
    }

    override fun compareDateTimeWithTzValues(
        airbyteMessageValue: String,
        destinationValue: String
    ): Boolean {
        // #13123 Normalization issue
        if (parseDestinationDateWithTz(destinationValue).isBefore(brokenDate)) {
            LOGGER.warn(
                "Validation is skipped due to known Normalization issue. Values older then 1583 year and with time zone stored wrongly(lose days)."
            )
            return true
        } else {
            return super.compareDateTimeWithTzValues(airbyteMessageValue, destinationValue)
        }
    }

    private val brokenDate: ZonedDateTime
        // #13123 Normalization issue
        get() = ZonedDateTime.of(1583, 1, 1, 0, 0, 0, 0, ZoneOffset.UTC)

    override fun compareObjects(expectedObject: JsonNode, actualObject: JsonNode) {
        val actualJsonNode =
            (if (actualObject.isTextual) deserialize(actualObject.textValue()) else actualObject)
        super.compareObjects(expectedObject, actualJsonNode)
    }

    companion object {
        private val LOGGER: Logger = LoggerFactory.getLogger(BigQueryTestDataComparator::class.java)
        private const val BIGQUERY_DATETIME_FORMAT = "yyyy-MM-dd'T'HH:mm:ss'Z'"
    }
}
