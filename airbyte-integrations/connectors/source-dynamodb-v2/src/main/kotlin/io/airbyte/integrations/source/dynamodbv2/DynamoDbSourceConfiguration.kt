/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.dynamodbv2

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
import java.net.URI
import java.time.Duration
import software.amazon.awssdk.regions.Region

/** DynamoDB-specific implementation of [SourceConfiguration]. */
data class DynamoDbSourceConfiguration(
    /**
     * Endpoint override (DynamoDB Local, VPC endpoint, ...); null for the regional AWS endpoint.
     */
    val endpoint: URI?,
    /** Null lets the AWS SDK resolve the region from its default provider chain. */
    val region: Region?,
    /** Both null when credentials come from the AWS SDK default provider chain. */
    val accessKeyId: String?,
    val secretAccessKey: String?,
    val reservedAttributeNames: List<String>,
    val ignoreMissingReadPermissionsTables: Boolean,
    override val maxConcurrency: Int,
    override val realHost: String,
    override val realPort: Int,
    /** DynamoDB syncs use per-stream state (no CDC / Global feed). */
    override val global: Boolean = false,
    override val maxSnapshotReadDuration: Duration? = null,
    override val checkpointTargetInterval: Duration = DEFAULT_CHECKPOINT_TARGET_INTERVAL,
    override val resourceAcquisitionHeartbeat: Duration = Duration.ofMillis(100L),
    /** SSH tunnels are not part of the DynamoDB spec. */
    override val sshTunnel: SshTunnelMethodConfiguration? = null,
    override val sshConnectionOptions: SshConnectionOptions =
        SshConnectionOptions.fromAdditionalProperties(emptyMap()),
) : SourceConfiguration {

    /** True when an access key id and secret were configured (and are not blank). */
    val hasStaticCredentials: Boolean
        get() = accessKeyId != null && secretAccessKey != null

    /** Keeps the secret out of logs. */
    override fun toString(): String =
        "DynamoDbSourceConfiguration(endpoint=$endpoint, region=$region, " +
            "accessKeyId=${accessKeyId?.let { "*****" }}, secretAccessKey=${secretAccessKey?.let { "*****" }}, " +
            "reservedAttributeNames=$reservedAttributeNames, " +
            "ignoreMissingReadPermissionsTables=$ignoreMissingReadPermissionsTables, " +
            "maxConcurrency=$maxConcurrency, checkpointTargetInterval=$checkpointTargetInterval)"

    /** Required to inject [DynamoDbSourceConfiguration] directly. */
    @Factory
    private class MicronautFactory {
        @Singleton
        fun dynamoDbSourceConfig(
            factory:
                SourceConfigurationFactory<
                    DynamoDbSourceConfigurationSpecification, DynamoDbSourceConfiguration>,
            supplier: ConfigurationSpecificationSupplier<DynamoDbSourceConfigurationSpecification>,
        ): DynamoDbSourceConfiguration = factory.make(supplier.get())
    }

    companion object {
        val DEFAULT_CHECKPOINT_TARGET_INTERVAL: Duration = Duration.ofMinutes(15)
        const val HTTPS_PORT = 443
        const val HTTP_PORT = 80
        /** Number of items the legacy connector sampled per table to infer its schema. */
        const val DISCOVER_SAMPLE_SIZE = 1000
    }
}

@Singleton
class DynamoDbSourceConfigurationFactory
@Inject
constructor(
    @Value("\${${DATA_CHANNEL_PROPERTY_PREFIX}.medium}") val dataChannelMedium: String = STDIO.name,
    @Value("\${${DATA_CHANNEL_PROPERTY_PREFIX}.socket-paths}")
    val socketPaths: List<String> = emptyList(),
) :
    SourceConfigurationFactory<
        DynamoDbSourceConfigurationSpecification, DynamoDbSourceConfiguration> {

    private val log = KotlinLogging.logger {}

    /**
     * The default implementation wraps every exception, including [ConfigErrorException], in a
     * generic "Failed to build ConnectorConfiguration." error, which hides the user-facing messages
     * thrown below. Let those through unchanged.
     */
    override fun make(spec: DynamoDbSourceConfigurationSpecification): DynamoDbSourceConfiguration =
        try {
            makeWithoutExceptionHandling(spec)
        } catch (e: ConfigErrorException) {
            throw e
        } catch (e: Exception) {
            throw ConfigErrorException("Failed to build ConnectorConfiguration.", e)
        }

    override fun makeWithoutExceptionHandling(
        pojo: DynamoDbSourceConfigurationSpecification,
    ): DynamoDbSourceConfiguration {
        val credentials: CredentialsSpecification =
            pojo.credentials
                ?: throw ConfigErrorException(
                    "Missing required 'credentials' property: choose 'Authenticate via Access Keys' " +
                        "or 'Role Based Authentication'.",
                )
        // Like the legacy connector, blank access keys fall back to the SDK default provider chain
        // (role-based access), whatever the selected `auth_type`.
        val (accessKeyId: String?, secretAccessKey: String?) =
            when (credentials) {
                is UserCredentialsSpecification -> {
                    val key: String? = credentials.accessKeyId.trim().ifBlank { null }
                    val secret: String? = credentials.secretAccessKey.trim().ifBlank { null }
                    if (key == null || secret == null) {
                        log.warn {
                            "Access key id or secret access key is blank; " +
                                "using the AWS default credentials provider chain instead."
                        }
                        null to null
                    } else {
                        key to secret
                    }
                }
                is RoleCredentialsSpecification -> null to null
            }

        val endpoint: URI? =
            pojo.endpoint
                ?.trim()
                ?.ifBlank { null }
                ?.let { raw: String ->
                    try {
                        URI.create(raw)
                    } catch (e: IllegalArgumentException) {
                        throw ConfigErrorException("Invalid endpoint '$raw': ${e.message}", e)
                    }
                }
        val region: Region? = pojo.region?.trim()?.ifBlank { null }?.let(Region::of)

        val reservedAttributeNames: List<String> =
            pojo.reservedAttributeNames
                ?.split(RESERVED_ATTRIBUTE_NAMES_SEPARATOR)
                ?.map(String::trim)
                ?.filter(String::isNotEmpty)
                ?: emptyList()

        val maxConcurrency: Int =
            when (DataChannelMedium.valueOf(dataChannelMedium)) {
                STDIO -> 1
                SOCKET -> socketPaths.size.coerceAtLeast(1)
            }
        log.info { "Effective concurrency: $maxConcurrency" }

        val (realHost: String, realPort: Int) = hostAndPort(endpoint, region)

        return DynamoDbSourceConfiguration(
            endpoint = endpoint,
            region = region,
            accessKeyId = accessKeyId,
            secretAccessKey = secretAccessKey,
            reservedAttributeNames = reservedAttributeNames,
            ignoreMissingReadPermissionsTables = pojo.ignoreMissingReadPermissionsTables ?: false,
            maxConcurrency = maxConcurrency,
            realHost = realHost,
            realPort = realPort,
        )
    }

    companion object {
        /** Same separator as the legacy connector. */
        val RESERVED_ATTRIBUTE_NAMES_SEPARATOR = Regex("\\s*,\\s*")

        /**
         * Host and port the connector talks to; only informational for this connector (the CDK uses
         * them for SSH tunnels, which the DynamoDB spec does not offer).
         */
        fun hostAndPort(endpoint: URI?, region: Region?): Pair<String, Int> {
            if (endpoint != null) {
                val host: String = endpoint.host ?: endpoint.toString()
                val port: Int =
                    when {
                        endpoint.port > 0 -> endpoint.port
                        endpoint.scheme.equals("http", ignoreCase = true) ->
                            DynamoDbSourceConfiguration.HTTP_PORT
                        else -> DynamoDbSourceConfiguration.HTTPS_PORT
                    }
                return host to port
            }
            val host: String =
                if (region != null) "dynamodb.${region.id()}.amazonaws.com"
                else "dynamodb.amazonaws.com"
            return host to DynamoDbSourceConfiguration.HTTPS_PORT
        }
    }
}
