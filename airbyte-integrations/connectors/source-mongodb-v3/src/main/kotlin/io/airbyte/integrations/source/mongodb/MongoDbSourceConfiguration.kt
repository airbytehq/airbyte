/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mongodb

import com.mongodb.MongoCredential
import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.command.CdcSourceConfiguration
import io.airbyte.cdk.command.SourceConfigurationFactory
import io.airbyte.cdk.ssh.SshConnectionOptions
import io.airbyte.cdk.ssh.SshNoTunnelMethod
import io.airbyte.cdk.ssh.SshTunnelMethodConfiguration
import jakarta.inject.Singleton
import java.time.Duration

data class MongoDbSourceConfiguration(
    override val maxConcurrency: Int,
    override val resourceAcquisitionHeartbeat: Duration,
    val connectionString: String,
    val queueSize: Int,
    val discoverSampleSize: Int,
    val captureMode: MongoDbSourceConfigurationFactory.CaptureMode,
    val mongoCredential: MongoCredential?,
    val schemaEnforced: Boolean,
    val initialWaitTime: Duration,
    val initialLoadTime: Duration,
    val invalidCdcCursorPositionBehavior:
        MongoDbSourceConfigurationFactory.InvalidCdcCursorPositionBehavior
) : CdcSourceConfiguration {
    override val global: Boolean = true

    // Following SSH configuration does not apply to MongoDB.
    override val realHost: String = ""
    override val realPort = 0
    override val sshTunnel: SshTunnelMethodConfiguration = SshNoTunnelMethod
    override val sshConnectionOptions: SshConnectionOptions =
        SshConnectionOptions.fromAdditionalProperties(mapOf())

    // In source-mongodb-v2 we don't allow user to set these configs. It may change in the future.
    override val debeziumHeartbeatInterval: Duration = Duration.ofMinutes(5)
    override val checkpointTargetInterval: Duration = Duration.ofMinutes(5)
}

@Singleton
class MongoDbSourceConfigurationFactory :
    SourceConfigurationFactory<
        MongoDbSourceConfigurationSpecification,
        MongoDbSourceConfiguration,
    > {

    fun buildConnectionString(input: String): String {
        val connectionString: String =
            input
                .trim()
                .replace(
                    DOUBLE_QUOTES_PATTERN.toRegex(),
                    "",
                )
                .replace(
                    CREDENTIALS_PLACEHOLDER.toRegex(),
                    "",
                )
        val builder = StringBuilder()
        builder.append(connectionString)
        return builder.toString()
    }
    override fun makeWithoutExceptionHandling(
        pojo: MongoDbSourceConfigurationSpecification,
    ): MongoDbSourceConfiguration {
        val clusterType: DatabaseClusterType = pojo.getDatabaseConfig()

        var connectionString: String
        var mongoCredential: MongoCredential?
        var schemaEnforced: Boolean

        when (clusterType) {
            is AtlasReplicaSet -> {
                connectionString = buildConnectionString(clusterType.connectionString)

                mongoCredential =
                    MongoCredential.createCredential(
                        clusterType.username,
                        clusterType.authSource,
                        clusterType.password.toCharArray(),
                    )
                schemaEnforced = clusterType.schemaEnforced
            }
            is SelfManagedReplicaSet -> {
                connectionString = buildConnectionString(clusterType.connectionString)
                if (
                    clusterType.username.isNullOrBlank() ||
                        clusterType.password.isNullOrBlank() ||
                        clusterType.authSource.isNullOrBlank()
                ) {
                    mongoCredential = null
                } else {
                    mongoCredential =
                        MongoCredential.createCredential(
                            clusterType.username!!,
                            clusterType.authSource!!,
                            clusterType.password!!.toCharArray(),
                        )
                }
                schemaEnforced = clusterType.schemaEnforced
            }
        }

        val captureMode: CaptureMode =
            when (pojo.updateCaptureMode) {
                "Lookup" -> CaptureMode.LOOKUP
                "Post Image" -> CaptureMode.POST_IMGAE
                else -> throw ConfigErrorException("Invalid capture mode")
            }

        return MongoDbSourceConfiguration(
            connectionString = connectionString,
            maxConcurrency = 1, // todo: Add this configuration to the spec.
            queueSize = pojo.queueSize ?: 10000,
            discoverSampleSize = pojo.discoverSampleSize ?: 10000,
            captureMode = captureMode,
            resourceAcquisitionHeartbeat =
                Duration.ofSeconds(pojo.initialWaitTimeInSeconds?.toLong() ?: 300),
            mongoCredential = mongoCredential,
            schemaEnforced = schemaEnforced,
            initialLoadTime = Duration.ofHours(pojo.initialLoadTimeoutHours?.toLong() ?: 8),
            initialWaitTime = Duration.ofSeconds(pojo.initialWaitTimeInSeconds?.toLong() ?: 300),
            invalidCdcCursorPositionBehavior =
                when (pojo.invalidCdcCursorPositionBehavior) {
                    "Fail sync" -> InvalidCdcCursorPositionBehavior.FAIL_SYNC
                    "Re-sync data" -> InvalidCdcCursorPositionBehavior.RESYNC_DATA
                    else -> throw ConfigErrorException("Invalid invalidCdcCursorPositionBehavior")
                },
        )
    }

    enum class CaptureMode() {
        LOOKUP,
        POST_IMGAE
    }

    enum class InvalidCdcCursorPositionBehavior(val displayName: String) {
        FAIL_SYNC("Fail sync"),
        RESYNC_DATA("Re-sync data")
    }
    companion object {
        const val DOUBLE_QUOTES_PATTERN = "\""
        const val CREDENTIALS_PLACEHOLDER = "<username>:<password>@"
    }
}
