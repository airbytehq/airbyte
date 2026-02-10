/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.message

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.load.data.AirbyteType
import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.data.AirbyteValueCoercer.DATE_TIME_FORMATTER
import io.airbyte.cdk.load.data.ArrayType
import io.airbyte.cdk.load.data.FieldType
import io.airbyte.cdk.load.data.IntegerType
import io.airbyte.cdk.load.data.IntegerValue
import io.airbyte.cdk.load.data.ObjectType
import io.airbyte.cdk.load.data.ObjectValue
import io.airbyte.cdk.load.data.StringType
import io.airbyte.cdk.load.data.StringValue
import io.airbyte.cdk.load.data.TimestampWithTimezoneValue
import io.airbyte.cdk.load.data.json.toAirbyteValue
import io.airbyte.cdk.load.util.deserializeToNode
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMeta
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMetaChange
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMetaChange.Reason
import java.math.BigInteger
import java.time.Instant
import java.time.OffsetDateTime
import java.time.ZoneOffset

data class Meta(
    val changes: List<Change> = mutableListOf(),
) {
    enum class AirbyteMetaFields(val fieldName: String, val type: AirbyteType) {
        RAW_ID(COLUMN_NAME_AB_RAW_ID, StringType),
        EXTRACTED_AT(COLUMN_NAME_AB_EXTRACTED_AT, IntegerType),
        META(
            COLUMN_NAME_AB_META,
            ObjectType(
                linkedMapOf(
                    "sync_id" to FieldType(IntegerType, nullable = false),
                    "changes" to
                        FieldType(
                            nullable = false,
                            type =
                                ArrayType(
                                    FieldType(
                                        nullable = false,
                                        type =
                                            ObjectType(
                                                linkedMapOf(
                                                    "field" to
                                                        FieldType(
                                                            StringType,
                                                            nullable = false,
                                                        ),
                                                    "change" to
                                                        FieldType(
                                                            StringType,
                                                            nullable = false,
                                                        ),
                                                    "reason" to
                                                        FieldType(
                                                            StringType,
                                                            nullable = false,
                                                        ),
                                                ),
                                            ),
                                    ),
                                ),
                        ),
                ),
            ),
        ),
        GENERATION_ID(COLUMN_NAME_AB_GENERATION_ID, IntegerType),
    }

    companion object {
        const val CHECKPOINT_ID_NAME: String = "partition_id"
        const val CHECKPOINT_INDEX_NAME: String = "id"

        const val AIRBYTE_META_SYNC_ID = "sync_id"
        const val AIRBYTE_META_CHANGES = "changes"

        const val COLUMN_NAME_AB_RAW_ID: String = "_airbyte_raw_id"
        const val COLUMN_NAME_AB_EXTRACTED_AT: String = "_airbyte_extracted_at"
        const val COLUMN_NAME_AB_META: String = "_airbyte_meta"
        const val COLUMN_NAME_AB_GENERATION_ID: String = "_airbyte_generation_id"
        const val COLUMN_NAME_DATA: String = "_airbyte_data"
        val COLUMN_NAMES =
            setOf(
                COLUMN_NAME_AB_RAW_ID,
                COLUMN_NAME_AB_EXTRACTED_AT,
                COLUMN_NAME_AB_META,
                COLUMN_NAME_AB_GENERATION_ID,
            )

        /**
         * A legacy column name. Destinations with "typing and deduping" used this in the raw tables
         * to indicate when a record went through T+D.
         */
        const val COLUMN_NAME_AB_LOADED_AT: String = "_airbyte_loaded_at"

        fun getMetaValue(metaColumnName: String, value: String): AirbyteValue {
            if (!COLUMN_NAMES.contains(metaColumnName)) {
                throw IllegalArgumentException("Invalid meta column name: $metaColumnName")
            }
            fun toObjectValue(value: JsonNode): AirbyteValue {
                if (value.isTextual) {
                    return toObjectValue(value.textValue().deserializeToNode())
                }
                return value.toAirbyteValue()
            }
            return when (metaColumnName) {
                COLUMN_NAME_AB_RAW_ID -> StringValue(value)
                COLUMN_NAME_AB_EXTRACTED_AT -> {
                    // Some destinations represent extractedAt as a long epochMillis,
                    // and others represent it as a timestamp string.
                    // Handle both cases here.
                    try {
                        IntegerValue(BigInteger(value))
                    } catch (_: Exception) {
                        TimestampWithTimezoneValue(
                            OffsetDateTime.parse(
                                value,
                                DATE_TIME_FORMATTER,
                            ),
                        )
                    }
                }
                COLUMN_NAME_AB_META -> toObjectValue(value.deserializeToNode())
                COLUMN_NAME_AB_GENERATION_ID -> IntegerValue(BigInteger(value))
                COLUMN_NAME_DATA -> toObjectValue(value.deserializeToNode())
                else ->
                    throw NotImplementedError(
                        "Column name $metaColumnName is not yet supported. This is probably a bug.",
                    )
            }
        }

        fun getEmittedAtMs(
            emittedAtMs: Long,
            extractedAtAsTimestampWithTimezone: Boolean
        ): AirbyteValue {
            return if (extractedAtAsTimestampWithTimezone) {
                TimestampWithTimezoneValue(
                    OffsetDateTime.ofInstant(Instant.ofEpochMilli(emittedAtMs), ZoneOffset.UTC)
                )
            } else {
                IntegerValue(emittedAtMs)
            }
        }
    }

    fun asProtocolObject(): AirbyteRecordMessageMeta =
        AirbyteRecordMessageMeta().withChanges(changes.map { change -> change.asProtocolObject() })

    data class Change(
        val field: String,
        // Using the raw protocol enums here.
        // By definition, we just want to pass these through directly.
        val change: AirbyteRecordMessageMetaChange.Change,
        val reason: Reason,
    ) {
        fun asProtocolObject(): AirbyteRecordMessageMetaChange =
            AirbyteRecordMessageMetaChange().withField(field).withChange(change).withReason(reason)
    }
}

fun Meta.Change.toAirbyteValue(): ObjectValue =
    ObjectValue(
        linkedMapOf(
            "field" to StringValue(field),
            "change" to StringValue(change.name),
            "reason" to StringValue(reason.name)
        )
    )

fun List<Meta.Change>.toAirbyteValues(): List<ObjectValue> = map { it.toAirbyteValue() }
