/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres

import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.Operation
import io.airbyte.cdk.check.CheckOperation
import io.airbyte.cdk.command.ConfigurationSpecificationSupplier
import io.airbyte.cdk.command.FeatureFlag
import io.airbyte.cdk.command.SourceConfigurationFactory
import io.airbyte.cdk.discover.MetadataQuerier
import io.airbyte.cdk.output.ExceptionHandler
import io.airbyte.cdk.output.OutputConsumer
import io.airbyte.cdk.ssh.SshNoTunnelMethod
import io.airbyte.integrations.source.postgres.config.EncryptionAllow
import io.airbyte.integrations.source.postgres.config.EncryptionDisable
import io.airbyte.integrations.source.postgres.config.EncryptionPrefer
import io.airbyte.integrations.source.postgres.config.PostgresSourceConfiguration
import io.airbyte.integrations.source.postgres.config.PostgresSourceConfigurationSpecification
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Replaces
import io.micronaut.context.annotation.Requires
import jakarta.inject.Singleton

/**
 * Postgres-specific check operation that validates SSL/SSH configuration on Airbyte Cloud before
 * building the full connector configuration. This ensures users get a clean
 * [AirbyteConnectionStatus.Status.FAILED] message when the SSL mode is insufficient for Cloud
 * deployment, instead of an exception that gets wrapped through the configuration construction
 * chain.
 *
 * The existing validation in [PostgresSourceConfigurationFactory] is left in place as a safety net
 * for read and discover operations.
 */
@Singleton
@Requires(property = Operation.PROPERTY, value = "check")
@Requires(env = ["source"])
@Replaces(CheckOperation::class)
class PostgresCheckOperation(
    private val configJsonObjectSupplier:
        ConfigurationSpecificationSupplier<PostgresSourceConfigurationSpecification>,
    private val configFactory:
        SourceConfigurationFactory<
            PostgresSourceConfigurationSpecification,
            out PostgresSourceConfiguration,
        >,
    private val metadataQuerierFactory: MetadataQuerier.Factory<PostgresSourceConfiguration>,
    private val outputConsumer: OutputConsumer,
    private val exceptionHandler: ExceptionHandler,
    private val featureFlags: Set<FeatureFlag>,
) : Operation {
    private val log = KotlinLogging.logger {}

    override fun execute() {
        try {
            log.info { "Parsing connector configuration JSON object." }
            val pojo: PostgresSourceConfigurationSpecification = configJsonObjectSupplier.get()
            log.info { "Validating SSL/SSH configuration." }
            validateSslConfiguration(pojo)
            log.info { "Building internal connector configuration object." }
            val config: PostgresSourceConfiguration = configFactory.make(pojo)
            log.info { "Connecting for config check." }
            metadataQuerierFactory.session(config).use {
                connectionCheck(it)
                it.extraChecks()
            }
        } catch (e: Exception) {
            log.debug(e) { "Exception while checking config." }
            val (errorTraceMessage, connectionStatusMessage) =
                exceptionHandler.handleCheckFailure(e)
            outputConsumer.accept(errorTraceMessage)
            outputConsumer.accept(connectionStatusMessage)
            log.info { "Config check failed." }
            return
        }
        log.info { "Config check completed successfully." }
        outputConsumer.accept(
            AirbyteConnectionStatus().withStatus(AirbyteConnectionStatus.Status.SUCCEEDED),
        )
    }

    /**
     * Validates that the SSL/SSH configuration is sufficient for Airbyte Cloud. Throws a
     * [ConfigErrorException] with a clear message if validation fails. This runs before config
     * construction so the error flows through [ExceptionHandler.handleCheckFailure] and surfaces as
     * a clean [AirbyteConnectionStatus.Status.FAILED] message.
     */
    private fun validateSslConfiguration(pojo: PostgresSourceConfigurationSpecification) {
        if (!featureFlags.contains(FeatureFlag.AIRBYTE_CLOUD_DEPLOYMENT)) {
            return
        }
        val encryption = pojo.getEncryptionValue()
        val tunnel = pojo.getTunnelMethodValue()
        if (
            encryption in listOf(EncryptionDisable, EncryptionAllow, EncryptionPrefer) &&
                tunnel is SshNoTunnelMethod
        ) {
            throw ConfigErrorException(
                "Connection from Airbyte Cloud requires SSL encryption or an SSH tunnel.",
            )
        }
    }

    /**
     * Checks the validity of the provided config by discovering the available tables and querying
     * at least one table successfully.
     */
    private fun connectionCheck(metadataQuerier: MetadataQuerier) {
        log.info { "Querying all stream names and namespaces." }
        var n = 0
        val namespaces: List<String?> = listOf<String?>(null) + metadataQuerier.streamNamespaces()
        for (namespace in namespaces) {
            for (streamID in metadataQuerier.streamNames(namespace)) {
                try {
                    metadataQuerier.fields(streamID)
                } catch (e: Exception) {
                    log.info(e) {
                        "Query failed on stream '${streamID.name}' " +
                            "in '${namespace ?: ""}': ${e.message}"
                    }
                    n++
                    continue
                }
                log.info {
                    "Query successful on stream '${streamID.name}' in '${namespace ?: ""}'."
                }
                return
            }
        }
        if (n == 0) {
            throw ConfigErrorException("Discovered zero tables.")
        } else {
            throw ConfigErrorException("Unable to query any of the $n discovered table(s).")
        }
    }
}
