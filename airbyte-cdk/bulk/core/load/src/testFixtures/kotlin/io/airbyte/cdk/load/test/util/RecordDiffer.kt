/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.test.util

import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.data.IntegerValue
import io.airbyte.cdk.load.data.NullValue
import io.airbyte.cdk.load.data.ObjectValue
import kotlin.reflect.jvm.jvmName

class RecordDiffer(
    /**
     * The path(s) to the primary key fields from a record. Most streams will have some `id`
     * field(s), even if they're not running in dedup mode. This comparator lets us match records
     * together to generate a more useful diff.
     *
     * In the rare case that a stream truly has no PK, the default value simply returns an empty
     * list.
     */
    val primaryKey: List<List<String>> = emptyList(),
    /** The path to the cursor from a record, or null if the stream has no cursor. */
    val cursor: List<String>? = null,
) {
    private fun extract(data: Map<String, AirbyteValue>, path: List<String>): AirbyteValue {
        return when (path.size) {
            0 -> throw IllegalArgumentException("Empty path")
            1 -> data[path.first()] ?: NullValue
            else -> {
                when (val next = data[path.first()]) {
                    null -> NullValue
                    is ObjectValue -> extract(next.values, path.subList(1, path.size))
                    else ->
                        throw IllegalArgumentException(
                            "Encountered non-map entry in path: $next at ${path.first()}"
                        )
                }
            }
        }
    }

    // if primaryKey is empty list, this always returns emptyList.
    private fun extractPrimaryKey(record: OutputRecord): List<AirbyteValue> {
        val pks = mutableListOf<AirbyteValue>()
        for (pkField in primaryKey) {
            pks.add(extract(record.data.values, pkField))
        }
        return pks
    }
    private fun extractCursor(record: OutputRecord): AirbyteValue {
        return extract(record.data.values, cursor!!)
    }

    /** Comparator that sorts records by their primary key */
    private val identityComparator: Comparator<OutputRecord> = Comparator { rec1, rec2 ->
        val pk1 = extractPrimaryKey(rec1)
        val pk2 = extractPrimaryKey(rec2)
        if (pk1.size != pk2.size) {
            throw IllegalStateException(
                "Records must have the same number of primary keys. Got $pk1 and $pk2."
            )
        }

        // Compare each PK field in order, until we find a field that the two records differ in.
        // If all the fields are equal, then these two records have the same PK.
        pk1.zip(pk2)
            .map { (pk1Field, pk2Field) -> valueComparator.compare(pk1Field, pk2Field) }
            .firstOrNull { it != 0 }
            ?: 0
    }

    /**
     * Comparator to sort records by their cursor (if there is one), breaking ties with extractedAt
     */
    private val sortComparator: Comparator<OutputRecord> =
        Comparator.comparing(
                { it: OutputRecord ->
                    (if (cursor == null) IntegerValue(0) else extractCursor(it))
                },
                valueComparator
            )
            .thenComparing { it -> it.extractedAt }

    /**
     * The actual comparator we'll use to sort the expected/actual record lists. I.e. group records
     * by their PK, then within each PK, sort by cursor/extractedAt.
     */
    private val everythingComparator = identityComparator.thenComparing(sortComparator)

    /** Returns a pretty-printed diff of the two lists, or null if they were identical */
    fun diffRecords(
        expectedRecords: List<OutputRecord>,
        actualRecords: List<OutputRecord>
    ): String? {
        val expectedRecordsSorted = expectedRecords.sortedWith(everythingComparator)
        val actualRecordsSorted = actualRecords.sortedWith(everythingComparator)

        // Match up all the records between the expected and actual records,
        // or if there's no matching record then detect that also.
        // We'll filter this list down to actual differing records later on.
        val matches = mutableListOf<MatchingRecords>()
        var expectedRecordIndex = 0
        var actualRecordIndex = 0
        while (
            expectedRecordIndex < expectedRecordsSorted.size &&
                actualRecordIndex < actualRecordsSorted.size
        ) {
            val expectedRecord = expectedRecords[expectedRecordIndex]
            val actualRecord = actualRecords[actualRecordIndex]
            val compare = everythingComparator.compare(expectedRecord, actualRecord)
            if (compare == 0) {
                // These records are the same underlying record
                matches.add(MatchingRecords(expectedRecord, actualRecord))
                expectedRecordIndex++
                actualRecordIndex++
            } else if (compare < 0) {
                // There's an extra expected record
                matches.add(MatchingRecords(expectedRecord, actualRecord = null))
                expectedRecordIndex++
            } else {
                // There's an extra actual record
                matches.add(MatchingRecords(expectedRecord = null, actualRecord))
                actualRecordIndex++
            }
        }

        // Tail loops in case we reached the end of one list before the other.
        while (expectedRecordIndex < expectedRecords.size) {
            matches.add(MatchingRecords(expectedRecords[expectedRecordIndex], actualRecord = null))
            expectedRecordIndex++
        }
        while (actualRecordIndex < actualRecords.size) {
            matches.add(MatchingRecords(expectedRecord = null, actualRecords[actualRecordIndex]))
            actualRecordIndex++
        }

        // We've paired up all the records, now find just the ones that are wrong.
        val diffs = matches.filter { it.isMismatch() }
        return if (diffs.isEmpty()) {
            null
        } else {
            diffs.joinToString("\n") { it.prettyPrintMismatch() }
        }
    }

    private inner class MatchingRecords(
        val expectedRecord: OutputRecord?,
        val actualRecord: OutputRecord?,
    ) {
        fun isMismatch(): Boolean =
            (expectedRecord == null && actualRecord != null) ||
                (expectedRecord != null && actualRecord == null) ||
                !recordsMatch(expectedRecord, actualRecord)

        fun prettyPrintMismatch(): String {
            return if (expectedRecord == null) {
                "Unexpected record (${generateRecordIdentifier(actualRecord!!)}): $actualRecord"
            } else if (actualRecord == null) {
                "Missing record (${generateRecordIdentifier(expectedRecord)}): $expectedRecord"
            } else {
                "Incorrect record (${generateRecordIdentifier(actualRecord)}):\n" +
                    generateDiffString(expectedRecord, actualRecord).prependIndent("  ")
            }
        }

        private fun recordsMatch(
            expectedRecord: OutputRecord?,
            actualRecord: OutputRecord?,
        ): Boolean =
            (expectedRecord == null && actualRecord == null) ||
                (expectedRecord != null &&
                    actualRecord != null &&
                    generateDiffString(expectedRecord, actualRecord).isEmpty())

        private fun generateRecordIdentifier(record: OutputRecord): String {
            // If the PK is an empty list, then don't include it
            val pk: List<AirbyteValue> = extractPrimaryKey(record)
            val pkString = if (pk.isEmpty()) "" else "pk=$pk"

            if (cursor != null) {
                val cursor: AirbyteValue = extractCursor(record)
                return "$pkString, cursor=$cursor"
            } else {
                return pkString
            }
        }

        private fun generateDiffString(
            expectedRecord: OutputRecord,
            actualRecord: OutputRecord,
        ): String {
            val diff: StringBuilder = StringBuilder()
            // Intentionally don't diff loadedAt / rawId, since those are generated dynamically by
            // the destination.
            if (expectedRecord.extractedAt != actualRecord.extractedAt) {
                diff.append(
                    "extractedAt: Expected ${expectedRecord.extractedAt}, got ${actualRecord.extractedAt}\n"
                )
            }
            if (expectedRecord.generationId != actualRecord.generationId) {
                diff.append(
                    "generationId: Expected ${expectedRecord.generationId}, got ${actualRecord.generationId}\n"
                )
            }
            if (expectedRecord.airbyteMeta != actualRecord.airbyteMeta) {
                diff.append(
                    "airbyteMeta: Expected ${expectedRecord.airbyteMeta}, got ${actualRecord.airbyteMeta}\n"
                )
            }

            // Diff the data. Iterate over all keys in the expected/actual records and compare their
            // values.
            val allDataKeys: Set<String> =
                expectedRecord.data.values.keys + actualRecord.data.values.keys
            allDataKeys.forEach { key ->
                val expectedPresent: Boolean = expectedRecord.data.values.containsKey(key)
                val actualPresent: Boolean = actualRecord.data.values.containsKey(key)
                if (expectedPresent && !actualPresent) {
                    // The expected record contained this key, but the actual record was missing
                    // this key.
                    diff.append(
                        "$key: Expected ${expectedRecord.data.values[key]}, but was <unset>\n"
                    )
                } else if (!expectedPresent && actualPresent) {
                    // The expected record didn't contain this key, but the actual record contained
                    // this key.
                    diff.append(
                        "$key: Expected <unset>, but was ${actualRecord.data.values[key]}\n"
                    )
                } else if (expectedPresent && actualPresent) {
                    // The expected and actual records both contain this key.
                    // Compare the values for equality.
                    // (actualPresent is always true here, but I think the if-tree is more readable
                    // with it explicitly in the condition)
                    val expectedValue = expectedRecord.data.values[key]
                    val actualValue = actualRecord.data.values[key]
                    if (expectedValue != actualValue) {
                        diff.append("$key: Expected $expectedValue, but was $actualValue\n")
                    }
                }
            }
            return diff.toString().trim()
        }
    }

    companion object {
        val valueComparator: Comparator<AirbyteValue> =
            Comparator.nullsFirst { v1, v2 -> compare(v1!!, v2!!) }

        private fun compare(v1: AirbyteValue, v2: AirbyteValue): Int {
            // when comparing values of different types, just sort by their class name.
            // in theory, we could check for numeric types and handle them smartly...
            // that's a lot of work though
            return if (v1::class != v2::class) {
                v1::class.jvmName.compareTo(v2::class.jvmName)
            } else {
                // otherwise, just be a terrible person.
                // we know these are the same type, so this is safe to do.
                @Suppress("UNCHECKED_CAST") (v1 as Comparable<AirbyteValue>).compareTo(v2)
            }
        }
    }
}
