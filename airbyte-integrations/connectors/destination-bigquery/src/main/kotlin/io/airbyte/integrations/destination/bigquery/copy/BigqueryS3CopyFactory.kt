/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.destination.bigquery.copy

import io.airbyte.cdk.Operation
import io.airbyte.cdk.SystemErrorException
import io.airbyte.cdk.load.config.DataChannelFormat
import io.airbyte.cdk.load.orchestration.db.legacy_typing_deduping.TableCatalogByDescriptor
import io.airbyte.integrations.destination.bigquery.spec.BigqueryConfiguration
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Factory
import io.micronaut.context.annotation.Value
import jakarta.inject.Named
import jakarta.inject.Singleton
import java.util.UUID

@Factory
class BigqueryS3CopyFactory {
    @Singleton
    fun create(
        @Value("\${${Operation.PROPERTY}}") operation: String,
        bigqueryConfiguration: BigqueryConfiguration,
        names: TableCatalogByDescriptor,
        configuredCatalog: ConfiguredAirbyteCatalog,
        @Named("dataChannelFormat") dataChannelFormat: DataChannelFormat,
    ): BigqueryS3Copy =
        // TEMPORARY preview routing. Remove this override before merging.
        // AWS bootstrap credentials must still be injected by the platform.
        createForOperation(
            operation,
            mapOf(
                "AIRBYTE_S3_COPY_ENABLED" to "true",
                "AIRBYTE_S3_COPY_BUCKET" to "sonar-entity-cache",
                "AIRBYTE_S3_COPY_REGION" to "us-east-2",
                "AIRBYTE_S3_COPY_ROLE_ARN" to
                    "arn:aws:iam::506572016262:role/fusion-snowflake-sync-copy",
                "AIRBYTE_S3_COPY_PREFIX" to "fusion",
                "AIRBYTE_S3_COPY_WORKSPACE_ID" to "00000000-0000-0000-0000-000000000000",
                "AIRBYTE_S3_COPY_SOURCE_ID" to "00000000-0000-0000-0000-000000000000",
                "AIRBYTE_S3_COPY_CONNECTION_ID" to "00000000-0000-0000-0000-000000000000",
            ),
        ) { config ->
            val runId = UUID.randomUUID()
            EnabledBigqueryS3Copy(
                config,
                bigqueryConfiguration,
                BigqueryCopyMetadata(
                    config,
                    bigqueryConfiguration,
                    names,
                    runId,
                    dataChannelFormat,
                    configuredCatalog,
                ),
                runId,
            )
        }

    companion object {
        /** Gate on the CLI operation, since the checker internally executes a WriteOperation. */
        internal fun createForOperation(
            operation: String,
            environment: Map<String, String> = System.getenv(),
            enabledFactory: (S3CopyConfiguration) -> BigqueryS3Copy,
        ): BigqueryS3Copy {
            if (operation != "write") return DisabledBigqueryS3Copy
            val config =
                try {
                    S3CopyConfiguration.fromEnvironment(environment)
                } catch (e: IllegalStateException) {
                    throw SystemErrorException(
                        "Invalid internal Fusion S3 archive configuration: ${e.message}",
                        e,
                    )
                }
            KotlinLogging.logger {}.info { "Fusion S3 copying enabled=${config != null}" }
            return config?.let(enabledFactory) ?: DisabledBigqueryS3Copy
        }
    }
}
