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
    val region: Region,
    /**
     * Endpoint override (DynamoDB Local, VPC endpoint, ...); null for the regional AWS endpoint.
     */
    val endpoint: URI?,
    val accessKeyId: String,
    val secretAccessKey: String,
    /** Set when the access key is a temporary credential issued by STS. */
    val sessionToken: String?,
    /**
     * IAM role to assume with the access key before reading DynamoDB; null to use the key as is.
     */
    val roleArn: String?,
    val externalId: String?,
    val reservedAttributeNames: List<String>,
    val ignoreMissingReadPermissionsTables: Boolean,
    /** Maximum number of items scanned per table during DISCOVER to infer its attributes. */
    val discoverSampleSize: Int,
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

    val assumesRole: Boolean
        get() = roleArn != null

    /** Keeps the secrets out of logs. */
    override fun toString(): String =
        "DynamoDbSourceConfiguration(region=$region, endpoint=$endpoint, accessKeyId=*****, " +
            "secretAccessKey=*****, sessionToken=${sessionToken?.let { "*****" }}, roleArn=$roleArn, " +
            "externalId=${externalId?.let { "*****" }}, reservedAttributeNames=$reservedAttributeNames, " +
            "ignoreMissingReadPermissionsTables=$ignoreMissingReadPermissionsTables, " +
            "discoverSampleSize=$discoverSampleSize, " +
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
            pojo.credentialsOrNull()
                ?: throw ConfigErrorException(
                    "Missing required 'credentials' property: choose 'Access Key' or " +
                        "'Access Key and IAM Role'.",
                )
        if (credentials is UnsupportedCredentialsSpecification) {
            throw ConfigErrorException(
                "Unsupported credentials type. Role based authentication (credentials from the " +
                    "environment the connector runs in) is not available; configure an access key, " +
                    "optionally with an IAM role to assume.",
            )
        }
        val accessKeyId: String =
            credentials.accessKeyId.trim().ifBlank {
                throw ConfigErrorException("The 'access_key_id' property must not be blank.")
            }
        val secretAccessKey: String =
            credentials.secretAccessKey.trim().ifBlank {
                throw ConfigErrorException("The 'secret_access_key' property must not be blank.")
            }
        val sessionToken: String? = credentials.sessionToken?.trim()?.ifBlank { null }
        val (roleArn: String?, externalId: String?) =
            when (credentials) {
                is AccessKeyCredentialsSpecification,
                is UnsupportedCredentialsSpecification -> null to null
                is AssumeRoleCredentialsSpecification -> {
                    val arn: String =
                        credentials.roleArn.trim().ifBlank {
                            throw ConfigErrorException("The 'role_arn' property must not be blank.")
                        }
                    if (!ROLE_ARN.matches(arn)) {
                        throw ConfigErrorException(
                            "'$arn' is not an IAM role ARN; expected " +
                                "arn:aws:iam::<account id>:role/<role name>.",
                        )
                    }
                    arn to credentials.externalId?.trim()?.ifBlank { null }
                }
            }

        val regionId: String =
            pojo.regionOrNull()?.trim()?.ifBlank { null }
                ?: throw ConfigErrorException("The 'region' property is required.")
        val region: Region = Region.of(regionId)
        if (region !in Region.regions()) {
            log.warn { "Region '$regionId' is not known to the AWS SDK; using it as configured." }
        }

        val endpoint: URI? = pojo.endpoint?.trim()?.ifBlank { null }?.let(::parseEndpoint)

        val reservedAttributeNames: List<String> =
            pojo.reservedAttributeNames
                ?.split(RESERVED_ATTRIBUTE_NAMES_SEPARATOR)
                ?.map(String::trim)
                ?.filter(String::isNotEmpty)
                ?: emptyList()

        val discoverSampleSize: Int =
            pojo.discoverSampleSize
                ?: DynamoDbSourceConfigurationSpecification.DEFAULT_DISCOVER_SAMPLE_SIZE
        if (
            discoverSampleSize !in
                DynamoDbSourceConfigurationSpecification
                    .MIN_DISCOVER_SAMPLE_SIZE..DynamoDbSourceConfigurationSpecification
                        .MAX_DISCOVER_SAMPLE_SIZE
        ) {
            throw ConfigErrorException(
                "'discover_sample_size' must be between " +
                    "${DynamoDbSourceConfigurationSpecification.MIN_DISCOVER_SAMPLE_SIZE} and " +
                    "${DynamoDbSourceConfigurationSpecification.MAX_DISCOVER_SAMPLE_SIZE}, got $discoverSampleSize.",
            )
        }

        val maxConcurrency: Int =
            when (DataChannelMedium.valueOf(dataChannelMedium)) {
                STDIO -> 1
                SOCKET -> socketPaths.size.coerceAtLeast(1)
            }
        log.info { "Effective concurrency: $maxConcurrency" }

        val (realHost: String, realPort: Int) = hostAndPort(endpoint, region)

        return DynamoDbSourceConfiguration(
            region = region,
            endpoint = endpoint,
            accessKeyId = accessKeyId,
            secretAccessKey = secretAccessKey,
            sessionToken = sessionToken,
            roleArn = roleArn,
            externalId = externalId,
            reservedAttributeNames = reservedAttributeNames,
            ignoreMissingReadPermissionsTables = pojo.ignoreMissingReadPermissionsTables ?: false,
            discoverSampleSize = discoverSampleSize,
            maxConcurrency = maxConcurrency,
            realHost = realHost,
            realPort = realPort,
        )
    }

    companion object {
        /** Same separator as the legacy connector. */
        val RESERVED_ATTRIBUTE_NAMES_SEPARATOR = Regex("\\s*,\\s*")

        /** `arn:<partition>:iam::<12-digit account>:role/<path/name>` */
        val ROLE_ARN = Regex("""arn:aws[a-z-]*:iam::\d{12}:role/.+""")

        /** An absolute http(s) URL with a host; anything else is a user error. */
        fun parseEndpoint(raw: String): URI {
            val uri: URI =
                try {
                    URI(raw)
                } catch (e: java.net.URISyntaxException) {
                    throw ConfigErrorException("Invalid endpoint '$raw': ${e.reason}", e)
                }
            val scheme: String? = uri.scheme?.lowercase()
            if ((scheme != "http" && scheme != "https") || uri.host == null) {
                throw ConfigErrorException(
                    "Invalid endpoint '$raw': expected a URL such as https://dynamodb.us-east-1.amazonaws.com.",
                )
            }
            return uri
        }

        /**
         * Host and port the connector talks to; only informational for this connector (the CDK uses
         * them for SSH tunnels, which the DynamoDB spec does not offer).
         */
        fun hostAndPort(endpoint: URI?, region: Region): Pair<String, Int> {
            if (endpoint != null) {
                val port: Int =
                    when {
                        endpoint.port > 0 -> endpoint.port
                        endpoint.scheme.equals("http", ignoreCase = true) ->
                            DynamoDbSourceConfiguration.HTTP_PORT
                        else -> DynamoDbSourceConfiguration.HTTPS_PORT
                    }
                return endpoint.host to port
            }
            return "dynamodb.${region.id()}.amazonaws.com" to DynamoDbSourceConfiguration.HTTPS_PORT
        }
    }
}
