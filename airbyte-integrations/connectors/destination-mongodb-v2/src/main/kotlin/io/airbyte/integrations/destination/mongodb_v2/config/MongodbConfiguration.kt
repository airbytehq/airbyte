/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mongodb_v2.config

import io.airbyte.cdk.load.command.DestinationConfiguration
import io.airbyte.cdk.load.command.DestinationConfigurationFactory
import jakarta.inject.Singleton

data class MongodbConfiguration(
    val connectionString: String,
    val database: String,
    val authSource: String,
    val batchSize: Int,
) : DestinationConfiguration() {
    val resolvedDatabase = database.ifEmpty { Defaults.DATABASE_NAME }
    val resolvedAuthSource = authSource.ifEmpty { Defaults.AUTH_SOURCE }
    val resolvedBatchSize = if (batchSize <= 0) Defaults.BATCH_SIZE else batchSize

    object Defaults {
        const val DATABASE_NAME = "airbyte"
        const val AUTH_SOURCE = "admin"
        const val BATCH_SIZE = 10_000
    }
}

@Singleton
class MongodbConfigurationFactory :
    DestinationConfigurationFactory<MongodbSpecification, MongodbConfiguration> {
    override fun makeWithoutExceptionHandling(
        pojo: MongodbSpecification
    ): MongodbConfiguration {
        return MongodbConfiguration(
            connectionString = pojo.connectionString,
            database = pojo.database,
            authSource = pojo.authSource ?: MongodbConfiguration.Defaults.AUTH_SOURCE,
            batchSize = pojo.batchSize ?: MongodbConfiguration.Defaults.BATCH_SIZE,
        )
    }
}
