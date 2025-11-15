/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.base.destination.typing_deduping

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ArrayNode
import com.fasterxml.jackson.databind.node.ObjectNode
import com.google.common.collect.Streams
import io.airbyte.commons.json.Jsons
import java.math.BigDecimal
import java.time.*
import java.time.format.DateTimeParseException
import java.util.*
import java.util.function.Function
import java.util.stream.Collectors
import java.util.stream.IntStream
import kotlin.Array
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.function.Executable

/**
 * Utility class to generate human-readable diffs between expected and actual records. Assumes 1s1t
 * output format.
 *
 * Prefer [io.airbyte.cdk.test.RecordDiffer], which operates on strongly-typed objects instead of
 * JsonNodes. This class is effectively deprecated; we're just keeping it around so that
 * [BaseTypingDedupingTest] and [BaseSqlGeneratorIntegrationTest] continue to function. Once those
 * classes are using the new RecordDiffer, we should remove this class.
 */
class LegacyRecordDiffer
@SafeVarargs
constructor(
    private val rawRecordColumnNames: Map<String, String>,
    private val finalRecordColumnNames: Map<String, String>,
    vararg identifyingColumns: Pair<ColumnId, AirbyteType>
) {
    private val rawRecordIdentityComparator: Comparator<JsonNode>
    private val rawRecordSortComparator: Comparator<JsonNode>
    private val rawRecordIdentityExtractor: Function<JsonNode, String>

    private val finalRecordIdentityComparator: Comparator<JsonNode>
    private val finalRecordSortComparator: Comparator<JsonNode>
    private val finalRecordIdentityExtractor: Function<JsonNode, String>

    /**
     * @param rawRecordColumnNames
     * @param finalRecordColumnNames
     * @param identifyingColumns Which fields constitute a unique record (typically PK+cursor). Do
     * _not_ include extracted_at; it is handled automatically.
     */
    init {
        val rawTableIdentifyingColumns: Array<Pair<String, AirbyteType>> =
            identifyingColumns.map { it.first.originalName to it.second }.toTypedArray()

        this.rawRecordIdentityComparator =
            buildIdentityComparator(rawTableIdentifyingColumns, rawRecordColumnNames)
        this.rawRecordSortComparator =
            rawRecordIdentityComparator.thenComparing { record: JsonNode ->
                asString(record[getMetadataColumnName(rawRecordColumnNames, "_airbyte_raw_id")])
            }
        this.rawRecordIdentityExtractor =
            buildIdentityExtractor(rawTableIdentifyingColumns, rawRecordColumnNames)

        val finalTableIdentifyingColumns: Array<Pair<String, AirbyteType>> =
            identifyingColumns.map { it.first.name to it.second }.toTypedArray()
        this.finalRecordIdentityComparator =
            buildIdentityComparator(finalTableIdentifyingColumns, finalRecordColumnNames)
        this.finalRecordSortComparator =
            finalRecordIdentityComparator.thenComparing { record: JsonNode ->
                asString(record[getMetadataColumnName(finalRecordColumnNames, "_airbyte_raw_id")])
            }
        this.finalRecordIdentityExtractor =
            buildIdentityExtractor(finalTableIdentifyingColumns, finalRecordColumnNames)
    }

    /**
     * In the expected records, a SQL null is represented as a JsonNode without that field at all,
     * and a JSON null is represented as a NullNode. For example, in the JSON blob {"name": null},
     * the `name` field is a JSON null, and the `address` field is a SQL null.
     */
    fun verifySyncResult(
        expectedRawRecords: List<JsonNode>,
        actualRawRecords: List<JsonNode>,
        expectedFinalRecords: List<JsonNode>,
        actualFinalRecords: List<JsonNode>
    ) {
        Assertions.assertAll(
            Executable { diffRawTableRecords(expectedRawRecords, actualRawRecords) },
            Executable { diffFinalTableRecords(expectedFinalRecords, actualFinalRecords) }
        )
    }

    fun diffRawTableRecords(expectedRecords: List<JsonNode>, actualRecords: List<JsonNode>) {
        val diff =
            diffRecords(
                expectedRecords.map { record: JsonNode -> this.deserializeMetaAndLiftData(record) },
                actualRecords.map { record: JsonNode -> this.deserializeMetaAndLiftData(record) },
                rawRecordIdentityComparator,
                rawRecordSortComparator,
                rawRecordIdentityExtractor,
                rawRecordColumnNames
            )

        if (!diff.isEmpty()) {
            Assertions.fail<Any>("Raw table was incorrect.\n$diff")
        }
    }

    fun diffFinalTableRecords(expectedRecords: List<JsonNode>, actualRecords: List<JsonNode>) {
        val diff =
            diffRecords(
                expectedRecords,
                actualRecords,
                finalRecordIdentityComparator,
                finalRecordSortComparator,
                finalRecordIdentityExtractor,
                finalRecordColumnNames
            )

        if (!diff.isEmpty()) {
            Assertions.fail<Any>("Final table was incorrect.\n$diff")
        }
    }

    /**
     * If airbyte_data/airbyte_meta are strings, deserialize them. Then lift _airbyte_data fields to
     * the root level.
     *
     * @return A copy of the record, but with all fields in _airbyte_data lifted to the top level.
     */
    private fun deserializeMetaAndLiftData(record: JsonNode): JsonNode {
        val copy = record.deepCopy<ObjectNode>()
        copy.remove(getMetadataColumnName(rawRecordColumnNames, "_airbyte_data"))
        var airbyteData = record[getMetadataColumnName(rawRecordColumnNames, "_airbyte_data")]
        if (airbyteData.isTextual) {
            airbyteData = Jsons.deserializeExact(airbyteData.asText())
        }
        Streams.stream(airbyteData.fields()).forEach { field: Map.Entry<String, JsonNode> ->
            if (!copy.has(field.key)) {
                copy.set<JsonNode>(field.key, field.value)
            } else {
                // This would only happen if the record has one of the metadata columns (e.g.
                // _airbyte_raw_id)
                // We don't support that in production, so we don't support it here either.
                throw RuntimeException(
                    "Cannot lift field " + field.key + " because it already exists in the record."
                )
            }
        }

        val metadataColumnName = getMetadataColumnName(rawRecordColumnNames, "_airbyte_meta")
        val airbyteMeta = record[metadataColumnName]
        if (airbyteMeta != null && airbyteMeta.isTextual) {
            copy.set<JsonNode>(metadataColumnName, Jsons.deserializeExact(airbyteMeta.asText()))
        }

        return copy
    }

    /**
     * Build a Comparator to detect equality between two records. It first compares all the
     * identifying columns in order, and breaks ties using extracted_at.
     */
    private fun buildIdentityComparator(
        identifyingColumns: Array<Pair<String, AirbyteType>>,
        columnNames: Map<String, String>
    ): Comparator<JsonNode> {
        // Start with a noop comparator for convenience
        var comp: Comparator<JsonNode> = Comparator.comparing { record -> 0 }
        for (column in identifyingColumns) {
            comp = comp.thenComparing { record -> extract(record!!, column.first, column.second) }
        }
        comp =
            comp.thenComparing { record ->
                asTimestampWithTimezone(
                    record!![getMetadataColumnName(columnNames, "_airbyte_extracted_at")]
                )
            }
        return comp
    }

    /** See [&lt;][.buildIdentityComparator] for an explanation of dataExtractor. */
    private fun buildIdentityExtractor(
        identifyingColumns: Array<Pair<String, AirbyteType>>,
        columnNames: Map<String, String>
    ): Function<JsonNode, String> {
        return Function { record: JsonNode ->
            (Arrays.stream(identifyingColumns)
                .map { column: Pair<String, AirbyteType> ->
                    getPrintableFieldIfPresent(record, column.first)
                }
                .collect(Collectors.joining(", ")) +
                getPrintableFieldIfPresent(
                    record,
                    getMetadataColumnName(columnNames, "_airbyte_extracted_at")
                ))
        }
    }

    /**
     * Generate a human-readable diff between the two lists. Assumes (in general) that two records
     * with the same PK, cursor, and extracted_at are the same record.
     *
     * Verifies that all values specified in the expected records are correct (_including_ raw_id),
     * and that no other fields are present (except for loaded_at and raw_id). We assume that it's
     * impossible to verify loaded_at, since it's generated dynamically; however, we do provide the
     * ability to assert on the exact raw_id if desired; we simply assume that raw_id is always
     * expected to be present.
     *
     * @param identityComparator Returns 0 iff two records are the "same" record (i.e. have the same
     * PK+cursor+extracted_at)
     * @param sortComparator Behaves identically to identityComparator, but if two records are the
     * same, breaks that tie using _airbyte_raw_id
     * @param recordIdExtractor Dump the record's PK+cursor+extracted_at into a human-readable
     * string
     * @return The diff, or empty string if there were no differences
     */
    private fun diffRecords(
        originalExpectedRecords: List<JsonNode>,
        originalActualRecords: List<JsonNode>,
        identityComparator: Comparator<JsonNode>,
        sortComparator: Comparator<JsonNode>,
        recordIdExtractor: Function<JsonNode, String>,
        columnNames: Map<String, String>
    ): String {
        val expectedRecords = originalExpectedRecords.sortedWith(sortComparator)
        val actualRecords = originalActualRecords.sortedWith(sortComparator)

        // Iterate through both lists in parallel and compare each record.
        // Build up an error message listing any incorrect, missing, or unexpected records.
        var message = ""
        var expectedRecordIndex = 0
        var actualRecordIndex = 0
        while (
            expectedRecordIndex < expectedRecords.size && actualRecordIndex < actualRecords.size
        ) {
            val expectedRecord = expectedRecords[expectedRecordIndex]
            val actualRecord = actualRecords[actualRecordIndex]
            val compare = identityComparator.compare(expectedRecord, actualRecord)
            if (compare == 0) {
                // These records should be the same. Find the specific fields that are different and
                // move on
                // to the next records in both lists.
                message +=
                    diffSingleRecord(recordIdExtractor, expectedRecord, actualRecord, columnNames)
                expectedRecordIndex++
                actualRecordIndex++
            } else if (compare < 0) {
                // The expected record is missing from the actual records. Print it and move on to
                // the next expected
                // record.
                message += "Row was expected but missing: $expectedRecord\n"
                expectedRecordIndex++
            } else {
                // There's an actual record which isn't present in the expected records. Print it
                // and move on to the
                // next actual record.
                message += "Row was not expected but present: $actualRecord\n"
                actualRecordIndex++
            }
        }
        // Tail loops in case we reached the end of one list before the other.
        while (expectedRecordIndex < expectedRecords.size) {
            message +=
                "Row was expected but missing: " + expectedRecords[expectedRecordIndex] + "\n"
            expectedRecordIndex++
        }
        while (actualRecordIndex < actualRecords.size) {
            message +=
                "Row was not expected but present: " + actualRecords[actualRecordIndex] + "\n"
            actualRecordIndex++
        }

        return message
    }

    private fun diffSingleRecord(
        recordIdExtractor: Function<JsonNode, String>,
        expectedRecord: JsonNode,
        actualRecord: JsonNode,
        columnNames: Map<String, String>
    ): String {
        var foundMismatch = false
        var mismatchedRecordMessage =
            "Row had incorrect data: " + recordIdExtractor.apply(expectedRecord) + "\n"
        // Iterate through each column in the expected record and compare it to the actual record's
        // value.
        for (column in Streams.stream<String>(expectedRecord.fieldNames()).sorted()) {
            // For all other columns, we can just compare their values directly.
            val expectedValue = expectedRecord[column]
            val actualValue = actualRecord[column]
            if (!areJsonNodesEquivalent(expectedValue, actualValue)) {
                mismatchedRecordMessage +=
                    generateFieldError("column $column", expectedValue, actualValue)
                foundMismatch = true
            }
        }
        // Then check the entire actual record for any columns that we weren't expecting.
        val extraColumns = checkForExtraOrNonNullFields(expectedRecord, actualRecord, columnNames)
        if (extraColumns.size > 0) {
            for ((key, value) in extraColumns) {
                mismatchedRecordMessage += generateFieldError("column $key", null, value)
                foundMismatch = true
            }
        }
        return if (foundMismatch) {
            mismatchedRecordMessage
        } else {
            ""
        }
    }

    /**
     * Verify that all fields in the actual record are present in the expected record. This is
     * primarily relevant for detecting fields that we expected to be null, but actually were not.
     * See [BaseTypingDedupingTest.dumpFinalTableRecords] for an explanation of how SQL/JSON nulls
     * are represented in the expected record.
     *
     * This has the side benefit of detecting completely unexpected columns, which would be a very
     * weird bug but is probably still useful to catch.
     */
    private fun checkForExtraOrNonNullFields(
        expectedRecord: JsonNode,
        actualRecord: JsonNode,
        columnNames: Map<String, String>
    ): LinkedHashMap<String, JsonNode> {
        val extraFields = LinkedHashMap<String, JsonNode>()
        for (column in Streams.stream<String>(actualRecord.fieldNames()).sorted()) {
            // loaded_at and raw_id are generated dynamically, so we just ignore them.
            val isLoadedAt = getMetadataColumnName(columnNames, "_airbyte_loaded_at") == column
            val isRawId = getMetadataColumnName(columnNames, "_airbyte_raw_id") == column
            val isExpected = expectedRecord.has(column)
            if (!(isLoadedAt || isRawId || isExpected)) {
                extraFields[column] = actualRecord[column]
            }
        }
        return extraFields
    }

    private fun getMetadataColumnName(
        columnNames: Map<String, String>,
        columnName: String
    ): String {
        return columnNames.getOrDefault(columnName, columnName)
    }

    companion object {
        private fun getPrintableFieldIfPresent(record: JsonNode, field: String): String {
            return if (record.has(field)) {
                field + "=" + record[field]
            } else {
                ""
            }
        }

        private fun areJsonNodesEquivalent(
            expectedValue: JsonNode?,
            actualValue: JsonNode?
        ): Boolean {
            return if (expectedValue == null || actualValue == null) {
                // If one of the values is null, then we expect both of them to be null.
                expectedValue == null && actualValue == null
            } else if (expectedValue is ArrayNode && actualValue is ArrayNode) {
                // If both values are arrays, compare each of their elements. Order should be
                // preserved
                IntStream.range(0, expectedValue.size()).allMatch { i: Int ->
                    areJsonNodesEquivalent(expectedValue[i], actualValue[i])
                }
            } else if (expectedValue is ObjectNode && actualValue is ObjectNode) {
                // If both values are objects compare their fields and values
                expectedValue.size() == actualValue.size() &&
                    expectedValue.fieldNames().asSequence().all { field: String ->
                        areJsonNodesEquivalent(expectedValue[field], actualValue[field])
                    }
            } else {
                // Otherwise, we need to compare the actual values.
                // This is kind of sketchy, but seems to work fine for the data we have in our test
                // cases.
                (expectedValue == actualValue ||
                    (expectedValue.isIntegralNumber &&
                        actualValue.isIntegralNumber &&
                        expectedValue.bigIntegerValue() == actualValue.bigIntegerValue()) ||
                    (expectedValue.isNumber &&
                        actualValue.isNumber &&
                        expectedValue.decimalValue() == actualValue.decimalValue()))
            }
        }

        /**
         * Produce a pretty-printed error message, e.g. " For column foo, expected 1 but got 2". The
         * leading spaces are intentional, to make the message easier to read when it's embedded in
         * a larger stacktrace.
         */
        private fun generateFieldError(
            fieldname: String,
            expectedValue: JsonNode?,
            actualValue: JsonNode?
        ): String {
            val expectedString = expectedValue?.toString() ?: "SQL NULL (i.e. no value)"
            val actualString = actualValue?.toString() ?: "SQL NULL (i.e. no value)"
            return "  For $fieldname, expected $expectedString but got $actualString\n"
        }

        // These asFoo methods are used for sorting records, so their defaults are intended to make
        // broken
        // records stand out.
        private fun asString(node: JsonNode?): String {
            return if (node == null || node.isNull) {
                ""
            } else if (node.isTextual) {
                node.asText()
            } else {
                Jsons.serialize(node)
            }
        }

        private fun asNumber(node: JsonNode?): BigDecimal {
            return if (node == null || !node.isNumber) {
                BigDecimal(Double.MIN_VALUE)
            } else {
                node.decimalValue()
            }
        }

        private fun asInt(node: JsonNode?): Long {
            return if (node == null || !node.isIntegralNumber) {
                Long.MIN_VALUE
            } else {
                node.longValue()
            }
        }

        private fun asBoolean(node: JsonNode?): Boolean {
            return if (node == null || !node.isBoolean) {
                false
            } else {
                node.asBoolean()
            }
        }

        private fun asTimestampWithTimezone(node: JsonNode?): Instant {
            return if (node == null || !node.isTextual) {
                Instant.ofEpochMilli(Long.MIN_VALUE)
            } else {
                try {
                    OffsetDateTime.parse(node.asText()).toInstant()
                } catch (parseE: DateTimeParseException) {
                    // Fallback to using LocalDateTime and try again
                    // Some databases have Timestamp_TZ mapped to TIMESTAMP with no offset,
                    // this is sketchy to assume it as always UTC
                    try {
                        LocalDateTime.parse(node.asText()).toInstant(ZoneOffset.UTC)
                    } catch (e: Exception) {
                        Instant.ofEpochMilli(Long.MIN_VALUE)
                    }
                } catch (e: Exception) {
                    Instant.ofEpochMilli(Long.MIN_VALUE)
                }
            }
        }

        private fun asTimestampWithoutTimezone(node: JsonNode?): LocalDateTime {
            return if (node == null || !node.isTextual) {
                LocalDateTime.ofInstant(Instant.ofEpochMilli(Long.MIN_VALUE), ZoneOffset.UTC)
            } else {
                try {
                    LocalDateTime.parse(node.asText())
                } catch (e: Exception) {
                    LocalDateTime.ofInstant(Instant.ofEpochMilli(Long.MIN_VALUE), ZoneOffset.UTC)
                }
            }
        }

        private fun asTimeWithTimezone(node: JsonNode?): OffsetTime {
            return if (node == null || !node.isTextual) {
                OffsetTime.of(0, 0, 0, 0, ZoneOffset.UTC)
            } else {
                OffsetTime.parse(node.asText())
            }
        }

        private fun asTimeWithoutTimezone(node: JsonNode?): LocalTime {
            return if (node == null || !node.isTextual) {
                LocalTime.of(0, 0, 0)
            } else {
                try {
                    LocalTime.parse(node.asText())
                } catch (e: Exception) {
                    LocalTime.of(0, 0, 0)
                }
            }
        }

        private fun asDate(node: JsonNode?): LocalDate {
            return if (node == null || !node.isTextual) {
                LocalDate.ofInstant(Instant.ofEpochMilli(Long.MIN_VALUE), ZoneOffset.UTC)
            } else {
                try {
                    LocalDate.parse(node.asText())
                } catch (e: Exception) {
                    LocalDate.ofInstant(Instant.ofEpochMilli(Long.MIN_VALUE), ZoneOffset.UTC)
                }
            }
        }

        private class Field(f: Comparable<*>) : Comparable<Field> {
            private val stringValue = f.toString()
            private val realType: Class<*> = f.javaClass
            override fun compareTo(o: Field): Int {
                if (realType.canonicalName == o.realType.canonicalName) {
                    return stringValue.compareTo(o.stringValue)
                }
                return realType.canonicalName.compareTo(o.realType.canonicalName)
            }
        }

        // Generics? Never heard of 'em. (I'm sorry)
        private fun extract(node: JsonNode, field: String, type: AirbyteType): Field {
            return Field(
                if (type is AirbyteProtocolType) {
                    when (type) {
                        AirbyteProtocolType.STRING -> asString(node[field])
                        AirbyteProtocolType.NUMBER -> asNumber(node[field])
                        AirbyteProtocolType.INTEGER -> asInt(node[field])
                        AirbyteProtocolType.BOOLEAN -> asBoolean(node[field])
                        AirbyteProtocolType.TIMESTAMP_WITH_TIMEZONE ->
                            asTimestampWithTimezone(node[field])
                        AirbyteProtocolType.TIMESTAMP_WITHOUT_TIMEZONE ->
                            asTimestampWithoutTimezone(node[field])
                        AirbyteProtocolType.TIME_WITH_TIMEZONE -> asTimeWithTimezone(node[field])
                        AirbyteProtocolType.TIME_WITHOUT_TIMEZONE ->
                            asTimeWithoutTimezone(node[field])
                        AirbyteProtocolType.DATE -> asDate(node[field])
                        AirbyteProtocolType.UNKNOWN -> node.toString()
                    }
                } else {
                    node.toString()
                }
            )
        }
    }
}
