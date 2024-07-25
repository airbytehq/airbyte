/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.debezium.internals

import com.google.common.collect.ImmutableSet

enum class SnapshotMetadata {
    FIRST,
    FIRST_IN_DATA_COLLECTION,
    LAST_IN_DATA_COLLECTION,
    TRUE,
    LAST,
    FALSE,
    NULL;

    companion object {
        private val ENTRIES_OF_SNAPSHOT_EVENTS: Set<SnapshotMetadata> =
            ImmutableSet.of(TRUE, FIRST, FIRST_IN_DATA_COLLECTION, LAST_IN_DATA_COLLECTION)
        private val STRING_TO_ENUM: MutableMap<String, SnapshotMetadata> = HashMap(12)

        init {
            STRING_TO_ENUM["true"] = TRUE
            STRING_TO_ENUM["TRUE"] = TRUE
            STRING_TO_ENUM["false"] = FALSE
            STRING_TO_ENUM["FALSE"] = FALSE
            STRING_TO_ENUM["last"] = LAST
            STRING_TO_ENUM["LAST"] = LAST
            STRING_TO_ENUM["first"] = FIRST
            STRING_TO_ENUM["FIRST"] = FIRST
            STRING_TO_ENUM["last_in_data_collection"] = LAST_IN_DATA_COLLECTION
            STRING_TO_ENUM["LAST_IN_DATA_COLLECTION"] = LAST_IN_DATA_COLLECTION
            STRING_TO_ENUM["first_in_data_collection"] = FIRST_IN_DATA_COLLECTION
            STRING_TO_ENUM["FIRST_IN_DATA_COLLECTION"] = FIRST_IN_DATA_COLLECTION
            STRING_TO_ENUM["NULL"] = NULL
            STRING_TO_ENUM["null"] = NULL
        }

        fun fromString(value: String): SnapshotMetadata? {
            if (STRING_TO_ENUM.containsKey(value)) {
                return STRING_TO_ENUM[value]
            }
            throw RuntimeException("ENUM value not found for $value")
        }

        fun isSnapshotEventMetadata(snapshotMetadata: SnapshotMetadata?): Boolean {
            return ENTRIES_OF_SNAPSHOT_EVENTS.contains(snapshotMetadata)
        }
    }
}
