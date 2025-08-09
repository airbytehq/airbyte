/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.test.util

import java.time.OffsetDateTime
import kotlin.test.assertEquals
import kotlin.test.assertNull
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

class RecordDifferTest {
    @Test
    fun testBasicBehavior() {
        val differ =
            RecordDiffer(
                primaryKey = listOf(listOf("id1"), listOf("id2")),
                cursor = listOf("updated_at"),
            )

        val diff =
            differ.diffRecords(
                expectedRecords =
                    listOf(
                        // Extra expected record
                        OutputRecord(
                            extractedAt = 1234,
                            generationId = 42,
                            mapOf(
                                "id1" to 1,
                                "id2" to 100,
                                "updated_at" to OffsetDateTime.parse("1970-01-01T00:00:00Z"),
                                "name" to "alice",
                                "phone" to "1234"
                            ),
                            airbyteMeta = null
                        ),
                        // Matching records
                        OutputRecord(
                            extractedAt = 1234,
                            generationId = 42,
                            mapOf(
                                "id1" to 1,
                                "id2" to 100,
                                "updated_at" to OffsetDateTime.parse("1970-01-01T00:00:01Z"),
                                "name" to "bob",
                            ),
                            airbyteMeta = null
                        ),
                        // Different records
                        OutputRecord(
                            extractedAt = 1234,
                            generationId = 42,
                            mapOf(
                                "id1" to 1,
                                "id2" to 100,
                                "updated_at" to OffsetDateTime.parse("1970-01-01T00:00:02Z"),
                                "name" to "charlie",
                                "phone" to "1234",
                                "email" to "charlie@example.com"
                            ),
                            airbyteMeta = OutputRecord.Meta(syncId = 42),
                        ),
                    ),
                actualRecords =
                    listOf(
                        // Matching records
                        OutputRecord(
                            extractedAt = 1234,
                            generationId = 42,
                            mapOf(
                                "id1" to 1,
                                "id2" to 100,
                                "updated_at" to OffsetDateTime.parse("1970-01-01T00:00:01Z"),
                                "name" to "bob",
                            ),
                            airbyteMeta = null
                        ),
                        // Different records
                        OutputRecord(
                            extractedAt = 1234,
                            generationId = 41,
                            mapOf(
                                "id1" to 1,
                                "id2" to 100,
                                "updated_at" to OffsetDateTime.parse("1970-01-01T00:00:02Z"),
                                "name" to "charlie",
                                "phone" to "5678",
                                "address" to "1234 charlie street"
                            ),
                            airbyteMeta = null
                        ),
                        // Extra actual record
                        OutputRecord(
                            extractedAt = 1234,
                            generationId = 42,
                            mapOf(
                                "id1" to 1,
                                "id2" to 100,
                                "updated_at" to OffsetDateTime.parse("1970-01-01T00:00:03Z"),
                                "name" to "dana",
                            ),
                            airbyteMeta = null
                        ),
                    ),
            )

        Assertions.assertEquals(
            """
            Missing record (pk=[IntegerValue(value=1), IntegerValue(value=100)], cursor=TimestampWithTimezoneValue(value=1970-01-01T00:00Z)): OutputRecord(rawId=null, extractedAt=1970-01-01T00:00:01.234Z, loadedAt=null, generationId=42, data=ObjectValue(values={id1=IntegerValue(value=1), id2=IntegerValue(value=100), updated_at=TimestampWithTimezoneValue(value=1970-01-01T00:00Z), name=StringValue(value=alice), phone=StringValue(value=1234)}), airbyteMeta=null)
            Incorrect record (pk=[IntegerValue(value=1), IntegerValue(value=100)], cursor=TimestampWithTimezoneValue(value=1970-01-01T00:00:02Z)):
              generationId: Expected 42, got 41
              airbyteMeta: Expected Meta(changes=[], syncId=42), got null
              phone: Expected StringValue(value=1234), but was StringValue(value=5678)
              email: Expected StringValue(value=charlie@example.com), but was <unset>
              address: Expected <unset>, but was StringValue(value=1234 charlie street)
            Unexpected record (pk=[IntegerValue(value=1), IntegerValue(value=100)], cursor=TimestampWithTimezoneValue(value=1970-01-01T00:00:03Z)): OutputRecord(rawId=null, extractedAt=1970-01-01T00:00:01.234Z, loadedAt=null, generationId=42, data=ObjectValue(values={id1=IntegerValue(value=1), id2=IntegerValue(value=100), updated_at=TimestampWithTimezoneValue(value=1970-01-01T00:00:03Z), name=StringValue(value=dana)}), airbyteMeta=null)
            """.trimIndent(),
            diff
        )
    }

    /** Verify that the differ can sort records which are identical other than the PK */
    @Test
    fun testSortPk() {
        val diff =
            RecordDiffer(primaryKey = listOf(listOf("id")), cursor = null)
                .diffRecords(
                    listOf(
                        OutputRecord(
                            extractedAt = 0,
                            generationId = 0,
                            data = mapOf("id" to 1, "name" to "foo"),
                            airbyteMeta = null,
                        ),
                        OutputRecord(
                            extractedAt = 0,
                            generationId = 0,
                            data = mapOf("id" to 2, "name" to "bar"),
                            airbyteMeta = null,
                        ),
                    ),
                    listOf(
                        OutputRecord(
                            extractedAt = 0,
                            generationId = 0,
                            data = mapOf("id" to 2, "name" to "bar"),
                            airbyteMeta = null,
                        ),
                        OutputRecord(
                            extractedAt = 0,
                            generationId = 0,
                            data = mapOf("id" to 1, "name" to "foo"),
                            airbyteMeta = null,
                        ),
                    )
                )
        assertNull(diff)
    }

    /** Verify that the differ can sort records which are identical other than the cursor */
    @Test
    fun testSortCursor() {
        val diff =
            RecordDiffer(primaryKey = listOf(listOf("id")), cursor = listOf("updated_at"))
                .diffRecords(
                    listOf(
                        OutputRecord(
                            extractedAt = 0,
                            generationId = 0,
                            data = mapOf("id" to 1, "name" to "foo", "updated_at" to 1),
                            airbyteMeta = null,
                        ),
                        OutputRecord(
                            extractedAt = 0,
                            generationId = 0,
                            data = mapOf("id" to 1, "name" to "bar", "updated_at" to 2),
                            airbyteMeta = null,
                        ),
                    ),
                    listOf(
                        OutputRecord(
                            extractedAt = 0,
                            generationId = 0,
                            data = mapOf("id" to 1, "name" to "bar", "updated_at" to 2),
                            airbyteMeta = null,
                        ),
                        OutputRecord(
                            extractedAt = 0,
                            generationId = 0,
                            data = mapOf("id" to 1, "name" to "foo", "updated_at" to 1),
                            airbyteMeta = null,
                        ),
                    ),
                )
        assertNull(diff)
    }

    /** Verify that the differ can sort records which are identical other than extractedAt */
    @Test
    fun testSortExtractedAt() {
        val diff =
            RecordDiffer(primaryKey = listOf(listOf("id")), cursor = null)
                .diffRecords(
                    listOf(
                        OutputRecord(
                            extractedAt = 0,
                            generationId = 0,
                            data = mapOf("id" to 1, "name" to "foo"),
                            airbyteMeta = null,
                        ),
                        OutputRecord(
                            extractedAt = 1,
                            generationId = 0,
                            data = mapOf("id" to 1, "name" to "bar"),
                            airbyteMeta = null,
                        ),
                    ),
                    listOf(
                        OutputRecord(
                            extractedAt = 1,
                            generationId = 0,
                            data = mapOf("id" to 1, "name" to "bar"),
                            airbyteMeta = null,
                        ),
                        OutputRecord(
                            extractedAt = 0,
                            generationId = 0,
                            data = mapOf("id" to 1, "name" to "foo"),
                            airbyteMeta = null,
                        ),
                    )
                )
        assertNull(diff)
    }

    @Test
    fun testNullEqualsUnset() {
        val diff =
            RecordDiffer(primaryKey = listOf(listOf("id")), cursor = null, nullEqualsUnset = true)
                .diffRecords(
                    listOf(
                        OutputRecord(
                            extractedAt = 1,
                            generationId = 0,
                            data =
                                mapOf(
                                    "id" to 1,
                                    "sub_object" to
                                        mapOf(
                                            "foo" to "bar",
                                            "sub_list" to listOf(mapOf<String, Any?>()),
                                        )
                                ),
                            airbyteMeta = null,
                        ),
                    ),
                    listOf(
                        OutputRecord(
                            extractedAt = 1,
                            generationId = 0,
                            data =
                                mapOf(
                                    "id" to 1,
                                    "name" to null,
                                    "sub_object" to
                                        mapOf(
                                            "foo" to "bar",
                                            "bar" to null,
                                            "sub_list" to listOf(mapOf("foo" to null)),
                                        )
                                ),
                            airbyteMeta = null,
                        ),
                    ),
                )
        assertNull(diff)
    }
}
