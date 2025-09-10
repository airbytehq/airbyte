/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.write.load

import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.orchestration.db.TableName
import io.airbyte.integrations.destination.snowflake.client.SnowflakeAirbyteClient
import io.github.oshai.kotlinlogging.KotlinLogging

private val logger = KotlinLogging.logger {}

class SnowflakeInsertBuffer(
    private val tableName: TableName,
    private val snowflakeClient: SnowflakeAirbyteClient
) {

    fun accumulate(recordFields: Map<String, AirbyteValue>) {
        recordFields.forEach {
            // TODO implement accumulation
        }
    }

    suspend fun flush() {
        logger.info { "Beginning insert into ${tableName.name}" }
        // TODO implement flush
        logger.info { "Finished insert of rows into ${tableName.name}" }
    }
}
