/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.mongodbv3.config

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
import io.airbyte.integrations.source.mongodbv3.config.MongoDbSourceConfigurationSpecification as Spec
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

/** An enum whose entries are selected in the spec by a human-readable [specValue]. */
interface SpecEnum {
    val specValue: String
}

/**
 * Resolves a spec string to an entry of [E], or throws a [ConfigErrorException] naming [property].
 */
inline fun <reified E> parseSpecEnum(property: String, value: String): E where
E : Enum<E>,
E : SpecEnum =
    enumValues<E>().firstOrNull { it.specValue == value }
        ?: throw ConfigErrorException(
            "Invalid value '$value' for $property, expected one of ${enumValues<E>().map { it.specValue }}.",
        )

/** What to do when the persisted change stream resume token is no longer valid. */
enum class InvalidCdcCursorPositionBehavior(override val specValue: String) : SpecEnum {
    FAIL_SYNC("Fail sync"),
    RESYNC_DATA("Re-sync data"),
}

/** How the change stream reports the new value of an updated document. */
enum class UpdateCaptureMode(override val specValue: String) : SpecEnum {
    LOOKUP("Lookup"),
    POST_IMAGE("Post Image"),
}

/** MongoDB-specific implementation of [SourceConfiguration]. */
data class MongoDbSourceConfiguration(
    val clusterType: MongoDbClusterType,
    /** Sanitized, see [MongoDbSourceConfigurationFactory.sanitizeConnectionString]. */
    val connectionString: String,
    val databases: List<String>,
    val username: String?,
    val password: String?,
    val authSource: String,
    val schemaEnforced: Boolean,
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

    /** `(username, password)` when both are configured, else null (no authentication). */
    val credential: Pair<String, String>?
        get() = if (username != null && password != null) username to password else null

    /** Required to inject [MongoDbSourceConfiguration] directly. */
    @Factory
    private class MicronautFactory {
        @Singleton
        fun mongoDbSourceConfig(
            factory: SourceConfigurationFactory<Spec, MongoDbSourceConfiguration>,
            supplier: ConfigurationSpecificationSupplier<Spec>,
        ): MongoDbSourceConfiguration = factory.make(supplier.get())
    }

    companion object {
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
) : SourceConfigurationFactory<Spec, MongoDbSourceConfiguration> {

    private val log = KotlinLogging.logger {}

    /**
     * The default `make` wraps every exception, [ConfigErrorException] included, in a generic
     * "Failed to build ConnectorConfiguration."; let the user-facing messages below through
     * unchanged.
     */
    override fun make(spec: Spec): MongoDbSourceConfiguration =
        try {
            makeWithoutExceptionHandling(spec)
        } catch (e: ConfigErrorException) {
            throw e
        } catch (e: Exception) {
            throw ConfigErrorException("Failed to build ConnectorConfiguration.", e)
        }

    override fun makeWithoutExceptionHandling(pojo: Spec): MongoDbSourceConfiguration {
        val databaseConfig: DatabaseConfigSpecification =
            pojo.databaseConfig
                ?: throw ConfigErrorException(
                    "Database configuration is missing required 'database_config' property.",
                )
        if (databaseConfig.databases.isEmpty()) {
            throw ConfigErrorException("No databases specified in the configuration.")
        }
        val connectionString: String = sanitizeConnectionString(databaseConfig.connectionString)
        val firstHost: String =
            try {
                ConnectionString(connectionString).hosts.first()
            } catch (e: IllegalArgumentException) {
                throw ConfigErrorException("Invalid connection string: ${e.message}", e)
            }
        val (realHost: String, realPort: Int) = splitHostAndPort(firstHost)

        val maxConcurrency: Int =
            when (DataChannelMedium.valueOf(dataChannelMedium)) {
                STDIO -> 1
                SOCKET -> socketPaths.size.coerceAtLeast(1)
            }
        log.info { "Effective concurrency: $maxConcurrency" }

        return MongoDbSourceConfiguration(
            clusterType =
                when (databaseConfig) {
                    is AtlasReplicaSetSpecification -> MongoDbClusterType.ATLAS_REPLICA_SET
                    is SelfManagedReplicaSetSpecification ->
                        MongoDbClusterType.SELF_MANAGED_REPLICA_SET
                },
            connectionString = connectionString,
            databases = databaseConfig.databases,
            username = databaseConfig.username,
            password = databaseConfig.password,
            authSource = databaseConfig.authSource ?: Spec.DEFAULT_AUTH_SOURCE,
            schemaEnforced = databaseConfig.schemaEnforced ?: true,
            discoverSampleSize = pojo.discoverSampleSize ?: Spec.DEFAULT_DISCOVER_SAMPLE_SIZE,
            discoverTimeout =
                Duration.ofSeconds(
                    (pojo.discoverTimeoutSeconds ?: Spec.DEFAULT_DISCOVER_TIMEOUT_SECONDS).toLong()
                ),
            invalidCdcCursorPositionBehavior =
                parseSpecEnum(
                    "invalid_cdc_cursor_position_behavior",
                    pojo.invalidCdcCursorPositionBehavior
                        ?: InvalidCdcCursorPositionBehavior.FAIL_SYNC.specValue,
                ),
            updateCaptureMode =
                parseSpecEnum(
                    "update_capture_mode",
                    pojo.updateCaptureMode ?: UpdateCaptureMode.LOOKUP.specValue,
                ),
            maxSnapshotReadDuration =
                Duration.ofHours(
                    (pojo.initialLoadTimeoutHours ?: Spec.DEFAULT_INITIAL_LOAD_TIMEOUT_HOURS)
                        .toLong()
                ),
            maxConcurrency = maxConcurrency,
            realHost = realHost,
            realPort = realPort,
        )
    }

    companion object {
        /** Placeholder that Atlas puts in copy-pasted connection strings. */
        const val CREDENTIALS_PLACEHOLDER = "<username>:<password>@"

        /**
         * Trims whitespace, drops stray quotes and the Atlas `<username>:<password>@` placeholder.
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
