/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.destination.s3.csv

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.integrations.base.JavaBaseConstants
import io.airbyte.commons.json.Jsons
import io.airbyte.protocol.models.v0.AirbyteRecordMessage
import java.time.Instant
import java.util.*

/**
 * A CsvSheetGenerator that produces data in the format expected by JdbcSqlOperations. See
 * JdbcSqlOperations#createTableQuery.
 *
 * This intentionally does not extend [BaseSheetGenerator], because it needs the columns in a
 * different order (ABID, JSON, timestamp) vs (ABID, timestamp, JSON)
 *
 * In 1s1t mode, the column ordering is also different (raw_id, extracted_at, loaded_at, data). Note
 * that the loaded_at column is rendered as an empty string; callers are expected to configure their
 * destination to parse this as NULL. For example, Snowflake's COPY into command accepts a NULL_IF
 * parameter, and Redshift accepts an EMPTYASNULL option.
 */
class StagingDatabaseCsvSheetGenerator
@JvmOverloads
constructor(private val useDestinationsV2Columns: Boolean = false) : CsvSheetGenerator {
    // TODO is this even used anywhere?
    private var header: List<String> =
        if (this.useDestinationsV2Columns) JavaBaseConstants.V2_RAW_TABLE_COLUMN_NAMES
        else JavaBaseConstants.LEGACY_RAW_TABLE_COLUMNS

    override fun getHeaderRow(): List<String> {
        return header
    }

    override fun getDataRow(id: UUID, recordMessage: AirbyteRecordMessage): List<Any> {
        return getDataRow(
            id,
            Jsons.serialize(recordMessage.data),
            recordMessage.emittedAt,
            Jsons.serialize(recordMessage.meta)
        )
    }

    override fun getDataRow(formattedData: JsonNode): List<Any> {
        return LinkedList<Any>(listOf(Jsons.serialize(formattedData)))
    }

    override fun getDataRow(
        id: UUID,
        formattedString: String,
        emittedAt: Long,
        formattedAirbyteMetaString: String
    ): List<Any> {
        return if (useDestinationsV2Columns) {
            java.util.List.of<Any>(
                id,
                Instant.ofEpochMilli(emittedAt),
                "",
                formattedString,
                formattedAirbyteMetaString
            )
        } else {
            java.util.List.of<Any>(id, formattedString, Instant.ofEpochMilli(emittedAt))
        }
    }
}
