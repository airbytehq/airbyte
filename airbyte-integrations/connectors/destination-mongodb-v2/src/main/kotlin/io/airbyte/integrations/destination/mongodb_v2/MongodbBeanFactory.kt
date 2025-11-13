/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mongodb_v2

import com.mongodb.ConnectionString
import com.mongodb.MongoClientSettings
import com.mongodb.client.MongoClient
import com.mongodb.client.MongoClients
import io.airbyte.cdk.Operation
import io.airbyte.cdk.load.orchestration.db.TempTableNameGenerator
import io.airbyte.integrations.destination.mongodb_v2.spec.MongodbConfiguration
import io.airbyte.integrations.destination.mongodb_v2.spec.MongodbConfigurationFactory
import io.airbyte.integrations.destination.mongodb_v2.spec.MongodbConfigurationSpecificationSupplier
import io.micronaut.context.annotation.Factory
import io.micronaut.context.annotation.Requires
import jakarta.inject.Singleton
import java.util.concurrent.TimeUnit

@Factory
class MongodbBeanFactory {

    @Singleton
    fun mongodbConfiguration(
        configFactory: MongodbConfigurationFactory,
        specFactory: MongodbConfigurationSpecificationSupplier,
    ): MongodbConfiguration {
        val spec = specFactory.get()
        return configFactory.make(spec)
    }

    @Singleton
    @Requires(property = Operation.PROPERTY, notEquals = "spec")
    fun mongoClient(config: MongodbConfiguration): MongoClient {
        // Build connection string with auth if provided
        val connectionString = buildConnectionString(config)

        val settings = MongoClientSettings.builder()
            .applyConnectionString(ConnectionString(connectionString))
            .applyToConnectionPoolSettings { builder ->
                builder.maxConnectionIdleTime(60, TimeUnit.SECONDS)
                builder.maxSize(20) // Max connections in pool
            }
            .applyToSocketSettings { builder ->
                builder.connectTimeout(30, TimeUnit.SECONDS)
                builder.readTimeout(30, TimeUnit.SECONDS)
            }
            .build()

        return MongoClients.create(settings)
    }

    @Singleton
    @Requires(property = Operation.PROPERTY, value = "spec")
    fun emptyMongoClient(): MongoClient {
        // Return a dummy client for spec operation (won't be used)
        return MongoClients.create("mongodb://localhost:27017")
    }

    @Singleton
    fun tempTableNameGenerator(config: MongodbConfiguration): TempTableNameGenerator {
        // Use default temp table name generator with internal namespace
        return io.airbyte.cdk.load.orchestration.db.DefaultTempTableNameGenerator(
            internalNamespace = "_airbyte_internal",
            affixLength = 8
        )
    }

    private fun buildConnectionString(config: MongodbConfiguration): String {
        val baseConnectionString = config.connectionString

        // If auth is configured, inject credentials into connection string
        if (config.authType == MongodbConfiguration.AuthType.LOGIN_PASSWORD &&
            !config.username.isNullOrBlank() &&
            !config.password.isNullOrBlank()
        ) {
            // Parse connection string and inject credentials
            // Format: mongodb://[username:password@]host:port/database
            val credentials = "${config.username}:${config.password}@"

            return if (baseConnectionString.startsWith("mongodb://")) {
                baseConnectionString.replace("mongodb://", "mongodb://$credentials")
            } else if (baseConnectionString.startsWith("mongodb+srv://")) {
                baseConnectionString.replace("mongodb+srv://", "mongodb+srv://$credentials")
            } else {
                // Credentials already in connection string or invalid format
                baseConnectionString
            }
        }

        return baseConnectionString
    }
}
