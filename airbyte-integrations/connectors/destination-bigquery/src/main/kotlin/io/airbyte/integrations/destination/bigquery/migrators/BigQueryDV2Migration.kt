/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery.migrators

import com.google.cloud.bigquery.BigQuery
import io.airbyte.integrations.base.destination.typing_deduping.DestinationHandler
import io.airbyte.integrations.base.destination.typing_deduping.DestinationInitialStatus
import io.airbyte.integrations.base.destination.typing_deduping.StreamConfig
import io.airbyte.integrations.base.destination.typing_deduping.migrators.Migration
import io.airbyte.integrations.destination.bigquery.BigQuerySQLNameTransformer
import io.airbyte.integrations.destination.bigquery.typing_deduping.BigQuerySqlGenerator
import io.airbyte.integrations.destination.bigquery.typing_deduping.BigQueryV1V2Migrator
import io.github.oshai.kotlinlogging.KotlinLogging
import kotlin.math.log

class BigQueryDV2Migration(private val sqlGenerator: BigQuerySqlGenerator, bigQuery: BigQuery) :
    Migration<BigQueryDestinationState> {
    private val log = KotlinLogging.logger {}
    private val legacyV1V2migrator = BigQueryV1V2Migrator(bigQuery, BigQuerySQLNameTransformer())
    override fun migrateIfNecessary(
        destinationHandler: DestinationHandler<BigQueryDestinationState>,
        stream: StreamConfig,
        state: DestinationInitialStatus<BigQueryDestinationState>
    ): Migration.MigrationResult<BigQueryDestinationState> {
        log.info { "Initializing DV2 Migration check" }
        legacyV1V2migrator.migrateIfNecessary(sqlGenerator, destinationHandler, stream)
        // Invalidate state because rawTableExists could be false but we don't use it yet for
        // anything ?
        return Migration.MigrationResult(BigQueryDestinationState(false), true)
    }
}
