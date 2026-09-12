/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.bigqueryv2

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.command.JdbcSourceConfiguration
import io.airbyte.cdk.command.SourceConfigurationFactory
import io.airbyte.cdk.output.DataChannelMedium
import io.airbyte.cdk.output.DataChannelMedium.SOCKET
import io.airbyte.cdk.output.DataChannelMedium.STDIO
import io.airbyte.cdk.output.sockets.DATA_CHANNEL_PROPERTY_PREFIX
import io.airbyte.cdk.ssh.SshConnectionOptions
import io.airbyte.cdk.ssh.SshNoTunnelMethod
import io.airbyte.cdk.ssh.SshTunnelMethodConfiguration
import io.airbyte.cdk.util.Jsons
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Value
import jakarta.inject.Inject
import jakarta.inject.Singleton
import java.time.Duration

private val log = KotlinLogging.logger {}

/**
 * BigQuery-specific implementation of [JdbcSourceConfiguration].
 *
 * The JDBC connection goes through Google's `google-cloud-bigquery-jdbc` driver; schema discovery
 * additionally uses the native `google-cloud-bigquery` client built from the same credentials (see
 * [BigQueryClientFactory]).
 */
data class BigQuerySourceConfiguration(
    val projectId: String,
    /** Contents of the service account key file. Never logged. */
    val credentialsJson: String,
    /** Configured `dataset_id`, or null to discover every dataset of the project. */
    val datasetId: String?,
    /**
     * Base URL of a BigQuery API emulator (e.g. `http://localhost:9050`), or null to use the real
     * service. Test-only, see [BigQueryEmulator].
     */
    val emulatorHost: String?,
    override val jdbcUrlFmt: String,
    override val jdbcProperties: Map<String, String>,
    override val maxConcurrency: Int,
    override val realHost: String,
    override val realPort: Int = DEFAULT_PORT,
    override val checkpointTargetInterval: Duration = DEFAULT_CHECKPOINT_TARGET_INTERVAL,
    override val resourceAcquisitionHeartbeat: Duration = Duration.ofMillis(100L),
    /** BigQuery is reached over HTTPS; SSH tunnels are not part of the spec. */
    override val sshTunnel: SshTunnelMethodConfiguration = SshNoTunnelMethod,
    override val sshConnectionOptions: SshConnectionOptions =
        SshConnectionOptions.fromAdditionalProperties(emptyMap()),
) : JdbcSourceConfiguration {

    /** No CDC: READ produces per-stream state. */
    override val global: Boolean = false
    override val maxSnapshotReadDuration: Duration? = null

    /** Datasets are the stream namespaces. Empty means every dataset of the project. */
    override val namespaces: Set<String> = setOfNotNull(datasetId)

    /**
     * Every SELECT is a BigQuery job, so probing each table with `SELECT ... LIMIT 0` during
     * discovery would be slow; table metadata is read with `tables.get` instead, which already
     * requires `bigquery.tables.get`.
     */
    override val checkPrivileges: Boolean = false

    /** Keeps the credentials out of logs. */
    override fun toString(): String =
        "BigQuerySourceConfiguration(projectId=$projectId, datasetId=$datasetId, " +
            "emulatorHost=$emulatorHost, jdbcUrlFmt=$jdbcUrlFmt, " +
            "jdbcProperties=${jdbcProperties.keys}, maxConcurrency=$maxConcurrency, " +
            "checkpointTargetInterval=$checkpointTargetInterval)"

    companion object {
        const val DEFAULT_PORT = 443
        const val BIGQUERY_API_HOST = "www.googleapis.com"
        const val BIGQUERY_API_URL = "https://$BIGQUERY_API_HOST/bigquery/v2:$DEFAULT_PORT"
        val DEFAULT_CHECKPOINT_TARGET_INTERVAL: Duration = Duration.ofMinutes(15)
    }
}

@Singleton
class BigQuerySourceConfigurationFactory
@Inject
constructor(
    @Value("\${${DATA_CHANNEL_PROPERTY_PREFIX}.medium}") val dataChannelMedium: String = STDIO.name,
    @Value("\${${DATA_CHANNEL_PROPERTY_PREFIX}.socket-paths}")
    val socketPaths: List<String> = emptyList(),
) :
    SourceConfigurationFactory<
        BigQuerySourceConfigurationSpecification, BigQuerySourceConfiguration> {

    /**
     * The default implementation wraps every exception, including [ConfigErrorException], in a
     * generic "Failed to build ConnectorConfiguration." error, which hides the user-facing messages
     * thrown below. Let those through unchanged.
     */
    override fun make(spec: BigQuerySourceConfigurationSpecification): BigQuerySourceConfiguration =
        try {
            makeWithoutExceptionHandling(spec)
        } catch (e: ConfigErrorException) {
            throw e
        } catch (e: Exception) {
            throw ConfigErrorException("Failed to build ConnectorConfiguration.", e)
        }

    override fun makeWithoutExceptionHandling(
        pojo: BigQuerySourceConfigurationSpecification,
    ): BigQuerySourceConfiguration {
        val projectId: String =
            pojo.projectIdOrNull()?.trim()?.takeIf { it.isNotEmpty() }
                ?: throw ConfigErrorException("Missing required 'project_id' property.")
        val credentialsJson: String =
            pojo.credentialsJsonOrNull()?.trim()?.takeIf { it.isNotEmpty() }
                ?: throw ConfigErrorException("Missing required 'credentials_json' property.")
        val datasetId: String? = pojo.datasetId?.trim()?.takeIf { it.isNotEmpty() }
        val emulatorHost: String? = BigQueryEmulator.hostOrNull()
        if (emulatorHost == null) {
            validateServiceAccountKey(credentialsJson)
        }

        val maxConcurrency: Int =
            when (DataChannelMedium.valueOf(dataChannelMedium)) {
                STDIO -> 1
                SOCKET -> socketPaths.size.coerceAtLeast(1)
            }
        log.info { "Effective concurrency: $maxConcurrency" }

        // The URL is logged by the CDK; secrets go into the JDBC properties instead.
        val jdbcProperties: MutableMap<String, String> = mutableMapOf("ProjectId" to projectId)
        val jdbcUrlFmt: String
        val realHost: String
        if (emulatorHost == null) {
            // OAuthType 0: service account; OAuthPvtKey accepts the raw JSON key contents.
            jdbcUrlFmt =
                "jdbc:bigquery://${BigQuerySourceConfiguration.BIGQUERY_API_URL};" +
                    "ProjectId=$projectId;OAuthType=0"
            jdbcProperties["OAuthPvtKey"] = credentialsJson
            realHost = BigQuerySourceConfiguration.BIGQUERY_API_HOST
        } else {
            // OAuthType 2: pre-generated token; the emulator does not authenticate requests.
            log.warn { "Connecting to the BigQuery emulator at $emulatorHost." }
            jdbcUrlFmt = "jdbc:bigquery://$emulatorHost;ProjectId=$projectId;OAuthType=2"
            jdbcProperties["OAuthAccessToken"] = BigQueryEmulator.DUMMY_ACCESS_TOKEN
            jdbcProperties["EndpointOverrides"] = "BIGQUERY=$emulatorHost"
            realHost = BigQuerySourceConfiguration.BIGQUERY_API_HOST
        }
        return BigQuerySourceConfiguration(
            projectId = projectId,
            credentialsJson = credentialsJson,
            datasetId = datasetId,
            emulatorHost = emulatorHost,
            jdbcUrlFmt = jdbcUrlFmt.replace("%", "%%"),
            jdbcProperties = jdbcProperties,
            maxConcurrency = maxConcurrency,
            realHost = realHost,
        )
    }

    companion object {
        const val SERVICE_ACCOUNT_TYPE = "service_account"

        /** Fails fast, with a precise message, on credentials the driver could not use. */
        fun validateServiceAccountKey(credentialsJson: String) {
            val node: JsonNode =
                try {
                    Jsons.readTree(credentialsJson)
                } catch (e: Exception) {
                    throw ConfigErrorException(
                        "'credentials_json' is not valid JSON: ${e.message?.lineSequence()?.first()}",
                        e,
                    )
                }
            if (!node.isObject) {
                throw ConfigErrorException("'credentials_json' must be a JSON object.")
            }
            val type: String? = node.get("type")?.asText()
            if (type != SERVICE_ACCOUNT_TYPE) {
                throw ConfigErrorException(
                    "'credentials_json' must be a service account key (\"type\": \"$SERVICE_ACCOUNT_TYPE\"), got \"type\": ${type?.let { "\"$it\"" } ?: "null"}.",
                )
            }
            for (required in listOf("client_email", "private_key")) {
                if (node.get(required)?.asText().isNullOrBlank()) {
                    throw ConfigErrorException(
                        "'credentials_json' is missing the '$required' property of a service account key.",
                    )
                }
            }
        }
    }
}

/**
 * Support for the `ghcr.io/goccy/bigquery-emulator` used by the tests. The emulator is selected
 * with the `BIGQUERY_EMULATOR_HOST` environment variable (the convention of Google's Go and Python
 * clients) or the `airbyte.source.bigquery.emulator-host` system property, which in-process tests
 * can set. Never set in production: credentials are not validated against an emulator.
 */
object BigQueryEmulator {
    const val ENV_VAR = "BIGQUERY_EMULATOR_HOST"
    const val SYSTEM_PROPERTY = "airbyte.source.bigquery.emulator-host"
    const val DUMMY_ACCESS_TOKEN = "emulator"

    fun hostOrNull(): String? =
        (System.getProperty(SYSTEM_PROPERTY) ?: System.getenv(ENV_VAR))
            ?.trim()
            ?.trimEnd('/')
            ?.takeIf { it.isNotEmpty() }
}
