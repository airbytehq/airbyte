/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.mongodb

import com.mongodb.ConnectionString
import com.mongodb.MongoClientSettings
import com.mongodb.MongoCredential
import com.mongodb.MongoDriverInformation
import com.mongodb.ReadPreference
import com.mongodb.client.MongoClient
import com.mongodb.client.MongoClients
import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.command.ConfigurationSpecificationSupplier
import io.airbyte.cdk.command.SourceConfiguration
import io.airbyte.cdk.command.SourceConfigurationFactory
import io.airbyte.cdk.ssh.SshConnectionOptions
import io.airbyte.cdk.ssh.SshTunnelMethodConfiguration
import io.micronaut.context.annotation.Factory
import jakarta.inject.Singleton
import java.net.URLEncoder
import java.nio.charset.StandardCharsets
import java.time.Duration

/** MongoDB-specific implementation of [SourceConfiguration] */
data class MongoDbSourceConfiguration(
    override val realHost: String,
    override val realPort: Int,
    override val sshTunnel: SshTunnelMethodConfiguration?,
    override val sshConnectionOptions: SshConnectionOptions,
    val connectionString: String,
    val database: String,
    val username: String?,
    val password: String?,
    val authSource: String,
    val discoverSampleSize: Int,
    override val maxConcurrency: Int,
    override val checkpointTargetInterval: Duration,
    override val resourceAcquisitionHeartbeat: Duration = Duration.ofMillis(100L),
) : SourceConfiguration {
    /** MongoDB source currently supports only snapshot reads (non-global state). */
    override val global: Boolean = false

    override val maxSnapshotReadDuration: Duration? = null

    /** Creates a MongoDB client for connecting to the database. */
    fun createMongoClient(): MongoClient {
        val mongoConnectionString = ConnectionString(connectionString)

        val mongoDriverInformation = MongoDriverInformation.builder()
            .driverName("Airbyte")
            .build()

        val mongoClientSettingsBuilder = MongoClientSettings.builder()
            .applyConnectionString(mongoConnectionString)

        if (mongoConnectionString.readPreference == null) {
            mongoClientSettingsBuilder.readPreference(ReadPreference.secondaryPreferred())
        }

        if (hasAuthCredentials()) {
            val encodedUser = URLEncoder.encode(username, StandardCharsets.UTF_8)
            mongoClientSettingsBuilder.credential(
                MongoCredential.createCredential(encodedUser, authSource, password!!.toCharArray())
            )
        }

        return MongoClients.create(mongoClientSettingsBuilder.build(), mongoDriverInformation)
    }

    fun hasAuthCredentials(): Boolean = !username.isNullOrBlank() && !password.isNullOrBlank()

    /** Required to inject [MongoDbSourceConfiguration] directly. */
    @Factory
    private class MicronautFactory {
        @Singleton
        fun mongoDbSourceConfig(
            factory:
                SourceConfigurationFactory<
                    MongoDbSourceConfigurationSpecification, MongoDbSourceConfiguration>,
            supplier: ConfigurationSpecificationSupplier<MongoDbSourceConfigurationSpecification>,
        ): MongoDbSourceConfiguration = factory.make(supplier.get())
    }
}

@Singleton
class MongoDbSourceConfigurationFactory :
    SourceConfigurationFactory<MongoDbSourceConfigurationSpecification, MongoDbSourceConfiguration> {

    override fun makeWithoutExceptionHandling(
        pojo: MongoDbSourceConfigurationSpecification,
    ): MongoDbSourceConfiguration {
        // Extract host and port from connection string for SSH tunnel support
        val (realHost, realPort) = extractHostAndPort(pojo.connectionString)

        val sshConnectionOptions: SshConnectionOptions =
            SshConnectionOptions.fromAdditionalProperties(pojo.getAdditionalProperties())

        val checkpointTargetInterval: Duration =
            Duration.ofSeconds(pojo.checkpointTargetIntervalSeconds?.toLong() ?: 300L)
        if (!checkpointTargetInterval.isPositive) {
            throw ConfigErrorException("Checkpoint Target Interval should be positive")
        }

        if (pojo.concurrency <= 0) {
            throw ConfigErrorException("Concurrency setting should be positive")
        }

        return MongoDbSourceConfiguration(
            realHost = realHost,
            realPort = realPort,
            sshTunnel = null, // MongoDB doesn't use SSH tunneling in the traditional JDBC sense
            sshConnectionOptions = sshConnectionOptions,
            connectionString = pojo.connectionString,
            database = pojo.database,
            username = pojo.username,
            password = pojo.password,
            authSource = pojo.authSource,
            discoverSampleSize = pojo.discoverSampleSize,
            maxConcurrency = pojo.concurrency,
            checkpointTargetInterval = checkpointTargetInterval,
        )
    }

    private fun extractHostAndPort(connectionString: String): Pair<String, Int> {
        return try {
            val mongoConnectionString = ConnectionString(connectionString)
            val hosts = mongoConnectionString.hosts
            if (hosts.isNotEmpty()) {
                val hostPort = hosts[0]
                if (hostPort.contains(":")) {
                    val parts = hostPort.split(":")
                    Pair(parts[0], parts[1].toInt())
                } else {
                    Pair(hostPort, 27017) // Default MongoDB port
                }
            } else {
                Pair("localhost", 27017)
            }
        } catch (e: Exception) {
            // Fallback for SRV connections or invalid strings
            Pair("localhost", 27017)
        }
    }
}
