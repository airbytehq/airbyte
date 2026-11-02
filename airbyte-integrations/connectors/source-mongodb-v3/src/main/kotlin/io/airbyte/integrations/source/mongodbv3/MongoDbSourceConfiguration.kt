/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.mongodbv3

import com.mongodb.ConnectionString
import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.command.ConfigurationSpecificationSupplier
import io.airbyte.cdk.command.SourceConfiguration
import io.airbyte.cdk.command.SourceConfigurationFactory
import io.airbyte.cdk.output.DataChannelMedium
import io.airbyte.cdk.output.DataChannelMedium.SOCKET
import io.airbyte.cdk.output.DataChannelMedium.STDIO
import io.airbyte.cdk.output.sockets.DATA_CHANNEL_PROPERTY_PREFIX
import io.airbyte.cdk.ssh.SshConnectionOptions
import io.airbyte.cdk.ssh.SshTunnelMethodConfiguration
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Factory
import io.micronaut.context.annotation.Value
import jakarta.inject.Inject
import jakarta.inject.Singleton
import java.time.Duration

enum class MongoDbClusterType {
    ATLAS_REPLICA_SET,
    SELF_MANAGED_REPLICA_SET,
}

/** What to do when the persisted change stream resume token is no longer valid. */
enum class InvalidCdcCursorPositionBehavior(val specValue: String) {
    FAIL_SYNC("Fail sync"),
    RESYNC_DATA("Re-sync data");

    companion object {
        fun fromSpecValue(value: String): InvalidCdcCursorPositionBehavior =
            entries.firstOrNull { it.specValue == value }
                ?: throw ConfigErrorException(
                    "Invalid value '$value' for invalid_cdc_cursor_position_behavior, " +
                        "expected one of ${entries.map { it.specValue }}.",
                )
    }
}

/** How the change stream reports the new value of an updated document. */
enum class UpdateCaptureMode(val specValue: String) {
    LOOKUP("Lookup"),
    POST_IMAGE("Post Image");

    companion object {
        fun fromSpecValue(value: String): UpdateCaptureMode =
            entries.firstOrNull { it.specValue == value }
                ?: throw ConfigErrorException(
                    "Invalid value '$value' for update_capture_mode, " +
                        "expected one of ${entries.map { it.specValue }}.",
                )
    }
}

/** MongoDB-specific implementation of [SourceConfiguration]. */
data class MongoDbSourceConfiguration(
    val clusterType: MongoDbClusterType,
    /**
     * Sanitized connection string, see [MongoDbSourceConfigurationFactory.sanitizeConnectionString]
     * .
     */
    val connectionString: String,
    val databases: List<String>,
    val username: String?,
    val password: String?,
    val authSource: String,
    val schemaEnforced: Boolean,
    val initialWaitingDuration: Duration,
    val queueSize: Int,
    val discoverSampleSize: Int,
    val discoverTimeout: Duration,
    val invalidCdcCursorPositionBehavior: InvalidCdcCursorPositionBehavior,
    val updateCaptureMode: UpdateCaptureMode,
    override val maxSnapshotReadDuration: Duration?,
    override val maxConcurrency: Int,
    override val realHost: String,
    override val realPort: Int,
    /** MongoDB incremental syncs are CDC-only: READ always produces GLOBAL state. */
    override val global: Boolean = true,
    override val checkpointTargetInterval: Duration = DEFAULT_CHECKPOINT_TARGET_INTERVAL,
    override val resourceAcquisitionHeartbeat: Duration = Duration.ofMillis(100L),
    /** SSH tunnels are not part of the MongoDB spec. */
    override val sshTunnel: SshTunnelMethodConfiguration? = null,
    override val sshConnectionOptions: SshConnectionOptions =
        SshConnectionOptions.fromAdditionalProperties(emptyMap()),
) : SourceConfiguration {

    val hasCredentials: Boolean
        get() = username != null && password != null

    /** Keeps the password out of logs. */
    override fun toString(): String =
        "MongoDbSourceConfiguration(clusterType=$clusterType, connectionString=$connectionString, " +
            "databases=$databases, username=$username, password=${if (password == null) "null" else "*****"}, " +
            "authSource=$authSource, schemaEnforced=$schemaEnforced, " +
            "initialWaitingDuration=$initialWaitingDuration, queueSize=$queueSize, " +
            "discoverSampleSize=$discoverSampleSize, discoverTimeout=$discoverTimeout, " +
            "invalidCdcCursorPositionBehavior=$invalidCdcCursorPositionBehavior, " +
            "updateCaptureMode=$updateCaptureMode, maxSnapshotReadDuration=$maxSnapshotReadDuration, " +
            "maxConcurrency=$maxConcurrency, checkpointTargetInterval=$checkpointTargetInterval)"

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

    companion object {
        /** Same cadence as the legacy connector's `SYNC_CHECKPOINT_DURATION`. */
        val DEFAULT_CHECKPOINT_TARGET_INTERVAL: Duration = Duration.ofMinutes(15)
        const val DEFAULT_MONGODB_PORT = 27017
    }
}

@Singleton
class MongoDbSourceConfigurationFactory
@Inject
constructor(
    @Value("\${${DATA_CHANNEL_PROPERTY_PREFIX}.medium}") val dataChannelMedium: String = STDIO.name,
    @Value("\${${DATA_CHANNEL_PROPERTY_PREFIX}.socket-paths}")
    val socketPaths: List<String> = emptyList(),
) :
    SourceConfigurationFactory<
        MongoDbSourceConfigurationSpecification, MongoDbSourceConfiguration> {

    private val log = KotlinLogging.logger {}

    /**
     * The default implementation wraps every exception, including [ConfigErrorException], in a
     * generic "Failed to build ConnectorConfiguration." error, which hides the user-facing messages
     * thrown below (and by the legacy connector). Let those through unchanged.
     */
    override fun make(spec: MongoDbSourceConfigurationSpecification): MongoDbSourceConfiguration =
        try {
            makeWithoutExceptionHandling(spec)
        } catch (e: ConfigErrorException) {
            throw e
        } catch (e: Exception) {
            throw ConfigErrorException("Failed to build ConnectorConfiguration.", e)
        }

    override fun makeWithoutExceptionHandling(
        pojo: MongoDbSourceConfigurationSpecification,
    ): MongoDbSourceConfiguration {
        val databaseConfig: DatabaseConfigSpecification =
            pojo.databaseConfigOrNull()
                ?: throw ConfigErrorException(
                    "Database configuration is missing required 'database_config' property.",
                )
        val databases: List<String> = databaseConfig.databases
        if (databases.isEmpty()) {
            throw ConfigErrorException("No databases specified in the configuration.")
        }
        val connectionString: String = sanitizeConnectionString(databaseConfig.connectionString)
        val parsedConnectionString: ConnectionString =
            try {
                ConnectionString(connectionString)
            } catch (e: IllegalArgumentException) {
                throw ConfigErrorException("Invalid connection string: ${e.message}", e)
            }
        val (realHost: String, realPort: Int) =
            splitHostAndPort(parsedConnectionString.hosts.first())

        val clusterType: MongoDbClusterType =
            when (databaseConfig) {
                is AtlasReplicaSetSpecification -> MongoDbClusterType.ATLAS_REPLICA_SET
                is SelfManagedReplicaSetSpecification -> MongoDbClusterType.SELF_MANAGED_REPLICA_SET
            }

        val queueSize: Int =
            (pojo.queueSize ?: MAX_QUEUE_SIZE).let { requested: Int ->
                val effective: Int = requested.coerceIn(MIN_QUEUE_SIZE, MAX_QUEUE_SIZE)
                if (effective != requested) {
                    log.warn {
                        "Requested queue_size $requested is out of range, using $effective."
                    }
                }
                effective
            }

        val maxConcurrency: Int =
            when (DataChannelMedium.valueOf(dataChannelMedium)) {
                STDIO -> 1
                SOCKET -> socketPaths.size.coerceAtLeast(1)
            }
        log.info { "Effective concurrency: $maxConcurrency" }

        return MongoDbSourceConfiguration(
            clusterType = clusterType,
            connectionString = connectionString,
            databases = databases,
            username = databaseConfig.username,
            password = databaseConfig.password,
            authSource = databaseConfig.authSource
                    ?: MongoDbSourceConfigurationSpecification.DEFAULT_AUTH_SOURCE,
            schemaEnforced = databaseConfig.schemaEnforced ?: true,
            initialWaitingDuration =
                Duration.ofSeconds(
                    (pojo.initialWaitingSeconds
                            ?: MongoDbSourceConfigurationSpecification
                                .DEFAULT_INITIAL_WAITING_SECONDS)
                        .toLong(),
                ),
            queueSize = queueSize,
            discoverSampleSize = pojo.discoverSampleSize
                    ?: MongoDbSourceConfigurationSpecification.DEFAULT_DISCOVER_SAMPLE_SIZE,
            discoverTimeout =
                Duration.ofSeconds(
                    (pojo.discoverTimeoutSeconds
                            ?: MongoDbSourceConfigurationSpecification
                                .DEFAULT_DISCOVER_TIMEOUT_SECONDS)
                        .toLong(),
                ),
            invalidCdcCursorPositionBehavior =
                InvalidCdcCursorPositionBehavior.fromSpecValue(
                    pojo.invalidCdcCursorPositionBehavior
                        ?: InvalidCdcCursorPositionBehavior.FAIL_SYNC.specValue,
                ),
            updateCaptureMode =
                UpdateCaptureMode.fromSpecValue(
                    pojo.updateCaptureMode ?: UpdateCaptureMode.LOOKUP.specValue,
                ),
            maxSnapshotReadDuration =
                Duration.ofHours(
                    (pojo.initialLoadTimeoutHours
                            ?: MongoDbSourceConfigurationSpecification
                                .DEFAULT_INITIAL_LOAD_TIMEOUT_HOURS)
                        .toLong(),
                ),
            maxConcurrency = maxConcurrency,
            realHost = realHost,
            realPort = realPort,
        )
    }

    companion object {
        /** Placeholder that Atlas puts in copy-pasted connection strings. */
        const val CREDENTIALS_PLACEHOLDER = "<username>:<password>@"

        /** Debezium event queue bounds, as in the legacy connector. */
        const val MIN_QUEUE_SIZE = 1_000
        const val MAX_QUEUE_SIZE = 10_000

        /**
         * Same normalization as the legacy connector: trims whitespace, drops stray double quotes
         * and the Atlas credentials placeholder (credentials are passed separately).
         */
        fun sanitizeConnectionString(raw: String): String =
            raw.trim().replace("\"", "").replace(CREDENTIALS_PLACEHOLDER, "")

        /** Splits a `host[:port]` seed, IPv6 literals included, defaulting to port 27017. */
        fun splitHostAndPort(hostAndPort: String): Pair<String, Int> {
            val closingBracket: Int = hostAndPort.lastIndexOf(']')
            val colon: Int = hostAndPort.lastIndexOf(':')
            if (colon < 0 || colon < closingBracket) {
                return hostAndPort to MongoDbSourceConfiguration.DEFAULT_MONGODB_PORT
            }
            val port: Int =
                hostAndPort.substring(colon + 1).toIntOrNull()
                    ?: MongoDbSourceConfiguration.DEFAULT_MONGODB_PORT
            return hostAndPort.substring(0, colon) to port
        }
    }
}
