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
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Factory
import jakarta.inject.Inject
import jakarta.inject.Singleton
import java.time.Duration
import org.apache.commons.lang3.RandomStringUtils

private val log = KotlinLogging.logger {}

class MsSqlServerSourceConfiguration(
    override val realHost: String,
    override val realPort: Int,
    override val sshTunnel: SshTunnelMethodConfiguration?,
    override val sshConnectionOptions: SshConnectionOptions,
    override val jdbcUrlFmt: String,
    override val jdbcProperties: Map<String, String>,
    override val namespaces: Set<String>,
    override val maxConcurrency: Int,
    override val resourceAcquisitionHeartbeat: Duration = Duration.ofMillis(100L),
    override val checkpointTargetInterval: Duration,
    //    override val debeziumHeartbeatInterval: Duration = Duration.ofSeconds(10),
    val incrementalReplicationConfiguration: IncrementalConfiguration,
) : JdbcSourceConfiguration {
    override val global = false
    override val maxSnapshotReadDuration: Duration? = null

    /** Required to inject [MsSqlServerSourceConfiguration] directly. */
    @Factory
    private class MicronautFactory {
        @Singleton
        fun mssqlServerSourceConfig(
            factory:
                SourceConfigurationFactory<
                    MsSqlServerSourceConfigurationSpecification, MsSqlServerSourceConfiguration>,
            supplier:
                ConfigurationSpecificationSupplier<MsSqlServerSourceConfigurationSpecification>,
        ): MsSqlServerSourceConfiguration = factory.make(supplier.get())
    }
}

sealed interface IncrementalConfiguration

data object UserDefinedCursorIncrementalConfiguration : IncrementalConfiguration

// data class CdcIncrementalConfiguration(
//    val initialWaitingSeconds: Duration,
//    val queueSize: Int,
//    val invalidCdcCursorPositionBehavior: InvalidCdcCursorPositionBehavior,
//    val initialLoadTimeout: Duration
// ) : IncrementalConfiguration
//
// enum class InvalidCdcCursorPositionBehavior {
//    FAIL_SYNC,
//    RESET_SYNC,
// }

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
        val incrementalSpec = pojo.getIncrementalValue()
        val incrementalReplicationConfiguration =
            when (incrementalSpec) {
                UserDefinedCursor -> UserDefinedCursorIncrementalConfiguration
                else ->
                    throw ConfigErrorException(
                        "Incremental configuration is not supported for MSSQL source"
                    )
            //                is Cdc -> {
            //                    val initialWaitingSeconds: Duration =
            //
            // Duration.ofSeconds(incrementalSpec.initialWaitingSeconds!!.toLong())
            //                    val initialLoadTimeout: Duration =
            //
            // Duration.ofHours(incrementalSpec.initialLoadTimeoutHours!!.toLong())
            //                    val queueSize = incrementalSpec.queueSize!!
            //                    val invalidCdcCursorPositionBehavior:
            // InvalidCdcCursorPositionBehavior =
            //                        if (incrementalSpec.invalidCdcCursorPositionBehavior == "Fail
            // sync") {
            //                            InvalidCdcCursorPositionBehavior.FAIL_SYNC
            //                        } else {
            //                            InvalidCdcCursorPositionBehavior.RESET_SYNC
            //                        }
            //                    CdcIncrementalConfiguration(
            //                        initialWaitingSeconds,
            //                        queueSize,
            //                        invalidCdcCursorPositionBehavior,
            //                        initialLoadTimeout,
            //                    )
            //                }
            }

        val sshTunnel: SshTunnelMethodConfiguration? = pojo.getTunnelMethodValue()
        val encryptionSpec: EncryptionSpecification? = pojo.getEncryptionValue()
        val jdbcEncryption =
            when (encryptionSpec) {
                is MsSqlServerEncryptionDisabledConfigurationSpecification,
                null -> {
                    if (
                        featureFlags.contains(FeatureFlag.AIRBYTE_CLOUD_DEPLOYMENT) &&
                            sshTunnel is SshNoTunnelMethod
                    ) {
                        throw ConfigErrorException(
                            "Connection from Airbyte Cloud requires " +
                                "SSL encryption or an SSH tunnel."
                        )
                    } else {
                        mapOf("encrypt" to "false", "trustServerCertificate" to "true")
                    }
                }
                is MsSqlServerEncryptionRequiredTrustServerCertificateConfigurationSpecification ->
                    mapOf("encrypt" to "true", "trustServerCertificate" to "true")
                is SslVerifyCertificate -> {
                    val certificate = encryptionSpec.certificate
                    val trustStoreProperties =
                        if (certificate == null) {
                            emptyMap()
                        } else {
                            val password = RandomStringUtils.secure().next(100)
                            val keyStoreUri =
                                SSLCertificateUtils.keyStoreFromCertificate(certificate, password)
                            mapOf(
                                "trustStore" to keyStoreUri.path,
                                "trustStorePassword" to password
                            )
                        }
                    val hostNameInCertificate = encryptionSpec.hostNameInCertificate
                    val hostNameProperties =
                        if (hostNameInCertificate == null) {
                            emptyMap()
                        } else {
                            mapOf("hostNameInCertificate" to hostNameInCertificate)
                        }
                    trustStoreProperties +
                        hostNameProperties +
                        mapOf("encrypt" to "true", "trustServerCertificate" to "false")
                }
            }

        return MsSqlServerSourceConfiguration(
            realHost = pojo.host,
            realPort = pojo.port,
            sshTunnel = sshTunnel,
            sshConnectionOptions = SshConnectionOptions.fromAdditionalProperties(emptyMap()),
            checkpointTargetInterval = Duration.ofHours(1),
            jdbcUrlFmt = "jdbc:sqlserver://%s:%d;databaseName=${pojo.database}",
            namespaces = pojo.schemas?.toSet() ?: setOf(),
            jdbcProperties =
                mapOf(
                        "user" to pojo.username,
                        "password" to pojo.password,
                    )
                    .plus(jdbcEncryption),
            maxConcurrency = 10,
            //            debeziumHeartbeatInterval = Duration.ofSeconds(15),
            resourceAcquisitionHeartbeat = Duration.ofSeconds(15),
            incrementalReplicationConfiguration = incrementalReplicationConfiguration
        )
    }
}
