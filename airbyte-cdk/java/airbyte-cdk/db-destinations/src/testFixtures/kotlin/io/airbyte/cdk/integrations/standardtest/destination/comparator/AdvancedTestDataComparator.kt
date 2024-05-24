/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.standardtest.destination.comparator

import com.fasterxml.jackson.databind.JsonNode
import io.github.oshai.kotlinlogging.KotlinLogging
import java.time.ZoneOffset
import java.time.ZonedDateTime
import java.time.format.DateTimeFormatter
import java.time.format.DateTimeParseException
import org.junit.jupiter.api.Assertions

private val LOGGER = KotlinLogging.logger {}

open class AdvancedTestDataComparator : TestDataComparator {
    override fun assertSameData(expected: List<JsonNode>, actual: List<JsonNode>) {
        LOGGER.info("Expected data {}", expected)
        LOGGER.info("Actual data   {}", actual)
        Assertions.assertEquals(expected.size, actual.size)
        val expectedIterator = expected.iterator()
        val actualIterator = actual.iterator()
        while (expectedIterator.hasNext() && actualIterator.hasNext()) {
            compareObjects(expectedIterator.next(), actualIterator.next())
        }
    }

    protected open fun resolveIdentifier(identifier: String?): List<String?> = listOf(identifier)

    protected open fun compareObjects(expectedObject: JsonNode, actualObject: JsonNode) {
        if (!areBothEmpty(expectedObject, actualObject)) {
            LOGGER.info("Expected Object : {}", expectedObject)
            LOGGER.info("Actual Object   : {}", actualObject)
            val expectedDataIterator = expectedObject.fields()
            while (expectedDataIterator.hasNext()) {
                val expectedEntry = expectedDataIterator.next()
                val expectedValue = expectedEntry.value
                val key = expectedEntry.key
                val actualValue =
                    ComparatorUtils.getActualValueByExpectedKey(key, actualObject) {
                        identifier: String? ->
                        this.resolveIdentifier(identifier)
                    }
                LOGGER.info("For {} Expected {} vs Actual {}", key, expectedValue, actualValue)
                assertSameValue(expectedValue, actualValue)
            }
        } else {
            LOGGER.info("Both rows are empty.")
        }
    }

    private fun isJsonNodeEmpty(jsonNode: JsonNode): Boolean {
        return jsonNode.isEmpty ||
            (jsonNode.size() == 1 && jsonNode.iterator().next().asText().isEmpty())
    }

    private fun areBothEmpty(expectedData: JsonNode, actualData: JsonNode): Boolean {
        return isJsonNodeEmpty(expectedData) && isJsonNodeEmpty(actualData)
    }

    // Allows subclasses to implement custom comparison asserts
    protected fun assertSameValue(expectedValue: JsonNode, actualValue: JsonNode?) {
        LOGGER.info("assertSameValue : {} vs {}", expectedValue, actualValue)

        Assertions.assertTrue(
            compareJsonNodes(expectedValue, actualValue),
            "Expected value $expectedValue vs Actual value $actualValue"
        )
    }

    protected fun compareJsonNodes(expectedValue: JsonNode?, actualValue: JsonNode?): Boolean {
        if (expectedValue == null || actualValue == null) {
            return expectedValue == null && actualValue == null
        } else if (isNumeric(expectedValue.asText())) {
            return compareNumericValues(expectedValue.asText(), actualValue.asText())
        } else if (expectedValue.isBoolean) {
            return compareBooleanValues(expectedValue.asText(), actualValue.asText())
        } else if (isDateTimeWithTzValue(expectedValue.asText())) {
            return compareDateTimeWithTzValues(expectedValue.asText(), actualValue.asText())
        } else if (isDateTimeValue(expectedValue.asText())) {
            return compareDateTimeValues(expectedValue.asText(), actualValue.asText())
        } else if (isDateValue(expectedValue.asText())) {
            return compareDateValues(expectedValue.asText(), actualValue.asText())
        } else if (isTimeWithTimezone(expectedValue.asText())) {
            return compareTimeWithTimeZone(expectedValue.asText(), actualValue.asText())
        } else if (isTimeWithoutTimezone(expectedValue.asText())) {
            return compareTimeWithoutTimeZone(expectedValue.asText(), actualValue.asText())
        } else if (expectedValue.isArray) {
            return compareArrays(expectedValue, actualValue)
        } else if (expectedValue.isObject) {
            compareObjects(expectedValue, actualValue)
            return true
        } else {
            LOGGER.warn("Default comparison method!")
            return compareString(expectedValue, actualValue)
        }
    }

    protected open fun compareString(expectedValue: JsonNode, actualValue: JsonNode): Boolean {
        return expectedValue.asText() == actualValue.asText()
    }

    private fun isNumeric(value: String): Boolean {
        return value.matches("-?\\d+(\\.\\d+)?".toRegex())
    }

    private fun getArrayList(jsonArray: JsonNode): MutableList<JsonNode> {
        val result: MutableList<JsonNode> = ArrayList()
        jsonArray.elements().forEachRemaining { e: JsonNode -> result.add(e) }
        return result
    }

    protected fun compareArrays(expectedArray: JsonNode, actualArray: JsonNode): Boolean {
        val expectedList: List<JsonNode> = getArrayList(expectedArray)
        val actualList = getArrayList(actualArray)

        if (expectedList.size != actualList.size) {
            return false
        } else {
            for (expectedNode in expectedList) {
                val sameActualNode =
                    actualList.firstOrNull { actualNode: JsonNode ->
                        compareJsonNodes(expectedNode, actualNode)
                    }
                if (sameActualNode != null) {
                    actualList.remove(sameActualNode)
                } else {
                    return false
                }
            }
            return true
        }
    }

    protected open fun compareBooleanValues(
        firstBooleanValue: String,
        secondBooleanValue: String
    ): Boolean {
        return firstBooleanValue.toBoolean() == secondBooleanValue.toBoolean()
    }

    protected fun compareNumericValues(
        firstNumericValue: String,
        secondNumericValue: String
    ): Boolean {
        val firstValue = firstNumericValue.toDouble()
        val secondValue = secondNumericValue.toDouble()

        return firstValue == secondValue
    }

    protected val airbyteDateTimeWithTzFormatter: DateTimeFormatter
        get() = DateTimeFormatter.ofPattern(AIRBYTE_DATETIME_WITH_TZ_FORMAT)

    protected val airbyteDateTimeParsedWithTzFormatter: DateTimeFormatter
        get() = DateTimeFormatter.ofPattern(AIRBYTE_DATETIME_PARSED_FORMAT_TZ)

    protected fun isDateTimeWithTzValue(value: String): Boolean {
        return !TEST_DATASET_IGNORE_LIST.contains(value) &&
            value.matches(
                "^\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}(\\.\\d+)?(Z|[+\\-]\\d{1,2}:\\d{2})( BC)?$".toRegex()
            )
    }

    protected open fun parseDestinationDateWithTz(destinationValue: String): ZonedDateTime {
        return ZonedDateTime.parse(
                destinationValue,
                DateTimeFormatter.ofPattern(AIRBYTE_DATETIME_WITH_TZ_FORMAT)
            )
            .withZoneSameInstant(ZoneOffset.UTC)
    }

    protected open fun compareDateTimeWithTzValues(
        airbyteMessageValue: String,
        destinationValue: String
    ): Boolean {
        try {
            val airbyteDate =
                ZonedDateTime.parse(airbyteMessageValue, airbyteDateTimeWithTzFormatter)
                    .withZoneSameInstant(ZoneOffset.UTC)
            val destinationDate = parseDestinationDateWithTz(destinationValue)
            return airbyteDate == destinationDate
        } catch (e: DateTimeParseException) {
            LOGGER.warn(
                "Fail to convert values to ZonedDateTime. Try to compare as text. Airbyte value({}), Destination value ({}). Exception: {}",
                airbyteMessageValue,
                destinationValue,
                e
            )
            return compareTextValues(airbyteMessageValue, destinationValue)
        }
    }

    protected fun isDateTimeValue(value: String): Boolean {
        return value.matches(
            "^\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}(\\.\\d+)?( BC)?$".toRegex()
        )
    }

    protected fun isTimeWithTimezone(value: String): Boolean {
        return value.matches("^\\d{2}:\\d{2}:\\d{2}(\\.\\d+)?(Z|[+\\-]\\d{1,2}:\\d{2})$".toRegex())
    }

    protected fun isTimeWithoutTimezone(value: String): Boolean {
        return value.matches("^\\d{2}:\\d{2}:\\d{2}(\\.\\d+)?$".toRegex())
    }

    protected open fun compareDateTimeValues(
        airbyteMessageValue: String,
        destinationValue: String
    ): Boolean {
        return compareTextValues(airbyteMessageValue, destinationValue)
    }

    protected fun isDateValue(value: String): Boolean {
        return value.matches("^\\d{4}-\\d{2}-\\d{2}( BC)?$".toRegex())
    }

    protected open fun compareDateValues(
        airbyteMessageValue: String,
        destinationValue: String
    ): Boolean {
        return compareTextValues(airbyteMessageValue, destinationValue)
    }

    protected open fun compareTimeWithoutTimeZone(
        airbyteMessageValue: String,
        destinationValue: String
    ): Boolean {
        return compareTextValues(airbyteMessageValue, destinationValue)
    }

    protected fun compareTimeWithTimeZone(
        airbyteMessageValue: String,
        destinationValue: String
    ): Boolean {
        return compareTextValues(airbyteMessageValue, destinationValue)
    }

    protected fun compareTextValues(firstValue: String, secondValue: String): Boolean {
        return firstValue == secondValue
    }

    companion object {

        const val AIRBYTE_DATE_FORMAT: String = "yyyy-MM-dd"
        const val AIRBYTE_DATETIME_FORMAT: String = "yyyy-MM-dd'T'HH:mm:ss"
        const val AIRBYTE_DATETIME_PARSED_FORMAT: String = "yyyy-MM-dd HH:mm:ss.S"
        const val AIRBYTE_DATETIME_PARSED_FORMAT_TZ: String = "yyyy-MM-dd HH:mm:ss XXX"
        const val AIRBYTE_DATETIME_WITH_TZ_FORMAT: String =
            ("[yyyy][yy]['-']['/']['.'][' '][MMM][MM][M]['-']['/']['.'][' '][dd][d]" +
                "[[' ']['T']HH:mm[':'ss[.][SSSSSS][SSSSS][SSSS][SSS][' '][z][zzz][Z][O][x][XXX][XX][X][' '][G]]]")

        // TODO revisit dataset which used date as string: exchange_rate_catalog.json
        // tried to change it to date time type but some connectors failed to store it e.i.
        // bigquery-denormalized
        private val TEST_DATASET_IGNORE_LIST =
            setOf(
                "2020-08-29T00:00:00Z",
                "2020-08-30T00:00:00Z",
                "2020-08-31T00:00:00Z",
                "2020-09-01T00:00:00Z",
                "2020-09-15T16:58:52.000000Z",
                "2020-03-31T00:00:00Z"
            )
    }
}
