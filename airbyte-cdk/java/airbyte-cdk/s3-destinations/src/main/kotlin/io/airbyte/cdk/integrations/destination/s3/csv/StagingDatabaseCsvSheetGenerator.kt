/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.destination.s3.csv

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.integrations.base.JavaBaseConstants
import io.airbyte.commons.json.Jsons
import io.airbyte.protocol.models.v0.AirbyteRecordMessage
import io.github.oshai.kotlinlogging.KotlinLogging
import java.time.Instant
import java.util.*

private val logger = KotlinLogging.logger {}

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
constructor(
    private val destinationColumns: JavaBaseConstants.DestinationColumns =
        JavaBaseConstants.DestinationColumns.LEGACY,
) : CsvSheetGenerator {
    override fun getHeaderRow(): List<String> {
        return destinationColumns.rawColumns
    }

    override fun getDataRow(
        id: UUID,
        recordMessage: AirbyteRecordMessage,
        generationId: Long,
        syncId: Long
    ): List<Any> {
        return getDataRow(
            id,
            Jsons.serialize(recordMessage.data),
            recordMessage.emittedAt,
            Jsons.serialize(recordMessage.meta),
            // Legacy code. Default to generation 0.
            0,
        )
    }

    override fun getDataRow(formattedData: JsonNode): List<Any> {
        return LinkedList<Any>(listOf(Jsons.serialize(formattedData)))
    }

    override fun getDataRow(
        id: UUID,
        formattedString: String,
        emittedAt: Long,
        formattedAirbyteMetaString: String,
        generationId: Long,
    ): List<Any> {
        return when (destinationColumns) {
            JavaBaseConstants.DestinationColumns.LEGACY ->
                listOf(id, formattedString, Instant.ofEpochMilli(emittedAt))
            JavaBaseConstants.DestinationColumns.V2_WITH_META ->
                listOf(
                    id,
                    Instant.ofEpochMilli(emittedAt),
                    "",
                    formattedString,
                    formattedAirbyteMetaString
                )
            JavaBaseConstants.DestinationColumns.V2_WITHOUT_META ->
                listOf(id, Instant.ofEpochMilli(emittedAt), "", formattedString)
            JavaBaseConstants.DestinationColumns.V2_WITH_GENERATION ->
                listOf(
                    id,
                    Instant.ofEpochMilli(emittedAt),
                    "",
                    formattedString,
                    formattedAirbyteMetaString,
                    generationId
                )
        }
    }
}
