/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mssql

import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.command.*
import io.airbyte.cdk.jdbc.SSLCertificateUtils
import io.airbyte.cdk.ssh.SshConnectionOptions
import io.airbyte.cdk.ssh.SshNoTunnelMethod
import io.airbyte.cdk.ssh.SshTunnelMethodConfiguration
import io.airbyte.integrations.source.mssql.config_spec.*
import io.micronaut.context.annotation.Factory
import jakarta.inject.Inject
import jakarta.inject.Singleton
import org.apache.commons.lang3.RandomStringUtils
import java.time.Duration


sealed interface MsSqlServerIncrementalReplicationConfiguration

data object MsSqlServerCursorBasedIncrementalReplicationConfiguration :
    MsSqlServerIncrementalReplicationConfiguration

data class MsSqlServerCdcIncrementalReplicationConfiguration(var initialWaitingSeconds: Int) :
    MsSqlServerIncrementalReplicationConfiguration

class MsSqlServerSourceConfiguration(
    override val realHost: String,
    override val realPort: Int,
    override val sshTunnel: SshTunnelMethodConfiguration?,
    override val sshConnectionOptions: SshConnectionOptions,
    override val global: Boolean,
    override val maxSnapshotReadDuration: Duration?,
    override val checkpointTargetInterval: Duration,
    override val maxConcurrency: Int,
    override val resourceAcquisitionHeartbeat: Duration,
    override val debeziumHeartbeatInterval: Duration,
    override val jdbcUrlFmt: String,
    override val jdbcProperties: Map<String, String>,
    override val namespaces: Set<String>,
    val databaseName: String,
    val incrementalReplicationConfiguration: MsSqlServerIncrementalReplicationConfiguration,
) : JdbcSourceConfiguration, CdcSourceConfiguration {}

@Singleton
class MsSqlServerSourceConfigurationFactory
@Inject
constructor(val featureFlags: Set<FeatureFlag>) :
    SourceConfigurationFactory<
        MsSqlServerSourceConfigurationSpecification, MsSqlServerSourceConfiguration> {

    constructor() : this(emptySet())

    override fun makeWithoutExceptionHandling(
        pojo: MsSqlServerSourceConfigurationSpecification,
    ): MsSqlServerSourceConfiguration {
        val replicationMethodPojo = pojo.replicationMethodJson
        val incrementalReplicationConfiguration =
            when (replicationMethodPojo) {
                is MsSqlServerCdcReplicationConfigurationSpecification ->
                    MsSqlServerCdcIncrementalReplicationConfiguration(
                        initialWaitingSeconds = replicationMethodPojo.initialWaitingSeconds
                                ?: MsSqlServerCdcReplicationConfigurationSpecification
                                    .DEFAULT_INITIAL_WAITING_SECONDS
                    )
                is MsSqlServerCursorBasedReplicationConfigurationSpecification ->
                    MsSqlServerCursorBasedIncrementalReplicationConfiguration
            }

        val sshTunnel: SshTunnelMethodConfiguration? = pojo.getTunnelMethodValue()
        val encryption: MsSqlServerEncryptionConfigurationSpecification? = pojo.getEncryptionValue()
        val jdbcEncryption =
            when (encryption) {
                is MsSqlServerEncryptionDisabledConfigurationSpecification, null -> {
                    if (
                        featureFlags.contains(FeatureFlag.AIRBYTE_CLOUD_DEPLOYMENT) &&
                        sshTunnel is SshNoTunnelMethod
                    ) {
                        throw ConfigErrorException(
                            "Connection from Airbyte Cloud requires " +
                                    "SSL encryption or an SSH tunnel."
                        )
                    } else {
                        mapOf("encrypt" to "false",
                            "trustServerCertificate" to "true")
                    }
                }

                is MsSqlServerEncryptionRequiredTrustServerCertificateConfigurationSpecification ->
                    mapOf("encrypt" to "true",
                        "trustServerCertificate" to "true")
                is SslVerifyCertificate -> {
                    val certificate = encryption.certificate
                    val trustStoreProperties =
                        if (certificate == null) {
                            emptyMap()
                        } else {
                            val password = RandomStringUtils.secure().next(100)
                            val keyStoreUri = SSLCertificateUtils.keyStoreFromCertificate(certificate, password)
                            mapOf(
                                "trustStore" to keyStoreUri.path,
                                "trustStorePassword" to password
                            )
                        }
                    val hostNameInCertificate = encryption.hostNameInCertificate
                    val hostNameProperties =
                        if (hostNameInCertificate == null) {
                            emptyMap()
                        } else {
                            mapOf("hostNameInCertificate" to hostNameInCertificate)
                        }
                    trustStoreProperties + hostNameProperties + mapOf(
                        "encrypt" to "true",
                        "trustServerCertificate" to "false"
                    )
                }
            }

        return MsSqlServerSourceConfiguration(
            realHost = pojo.host,
            realPort = pojo.port,
            sshTunnel = sshTunnel,
            sshConnectionOptions = SshConnectionOptions.fromAdditionalProperties(emptyMap()),
            global =
                incrementalReplicationConfiguration
                    is MsSqlServerCdcIncrementalReplicationConfiguration,
            maxSnapshotReadDuration = null,
            checkpointTargetInterval = Duration.ofHours(1),
            jdbcUrlFmt = "jdbc:sqlserver://%s:%d;databaseName=${pojo.database}",
            namespaces = pojo.schemas?.toSet() ?: setOf(),
            jdbcProperties =
                mapOf("user" to pojo.username, "password" to pojo.password, "databaseName" to pojo.database).plus(jdbcEncryption),
            maxConcurrency = 10,
            debeziumHeartbeatInterval = Duration.ofSeconds(15),
            resourceAcquisitionHeartbeat = Duration.ofSeconds(15),
            databaseName = pojo.database,
            incrementalReplicationConfiguration = incrementalReplicationConfiguration
        )
    }

    /** Required to inject [MysqlSourceConfiguration] directly. */
    @Factory
    private class MicronautFactory {
        @Singleton
        fun mysqlSourceConfig(
            factory:
                SourceConfigurationFactory<
                    MsSqlServerSourceConfigurationSpecification, MsSqlServerSourceConfiguration>,
            supplier:
                ConfigurationSpecificationSupplier<MsSqlServerSourceConfigurationSpecification>,
        ): MsSqlServerSourceConfiguration = factory.make(supplier.get())
    }
}
