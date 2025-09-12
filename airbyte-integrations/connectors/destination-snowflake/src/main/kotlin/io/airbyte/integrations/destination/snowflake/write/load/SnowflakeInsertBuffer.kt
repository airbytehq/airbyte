/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.write.load

import com.google.common.annotations.VisibleForTesting
import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.orchestration.db.TableName
import io.airbyte.integrations.destination.snowflake.client.SnowflakeAirbyteClient
import io.github.oshai.kotlinlogging.KotlinLogging
import java.util.concurrent.BlockingQueue
import java.util.concurrent.LinkedBlockingQueue

private val logger = KotlinLogging.logger {}

class SnowflakeInsertBuffer(
    private val tableName: TableName,
    private val snowflakeClient: SnowflakeAirbyteClient
) {

    @VisibleForTesting
    internal val recordQueue: BlockingQueue<Map<String, AirbyteValue>> = LinkedBlockingQueue()

    fun accumulate(recordFields: Map<String, AirbyteValue>) {
        recordQueue.offer(recordFields)
    }

    suspend fun flush() {
        logger.info { "Beginning insert into ${tableName.name}" }
        // First, get all accumulated records
        val records = mutableListOf<Map<String, AirbyteValue>>()
        recordQueue.drainTo(records)

        if (records.isEmpty()) {
            logger.info { "No records to insert into ${tableName.name}" }
            return
        }

        // Use the new ingest client method to insert records directly
        val response = snowflakeClient.insertRecordsUsingIngestClient(tableName, records)

        if (response.hasErrors()) {
            logger.error {
                "Failed to insert records into ${tableName.name}. Errors: ${response.insertErrors}"
            }
            throw RuntimeException("Insert operation failed with errors: ${response.insertErrors}")
        }

        logger.info { "Finished insert of ${records.size} row(s) into ${tableName.name}" }
    }
}
