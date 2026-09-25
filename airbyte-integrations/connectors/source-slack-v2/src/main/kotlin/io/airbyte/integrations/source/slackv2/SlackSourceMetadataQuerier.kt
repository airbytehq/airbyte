/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.slackv2

import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.Operation
import io.airbyte.cdk.StreamIdentifier
import io.airbyte.cdk.discover.EmittedField
import io.airbyte.cdk.discover.MetadataQuerier
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Primary
import io.micronaut.context.annotation.Value
import jakarta.inject.Inject
import jakarta.inject.Singleton
import kotlinx.coroutines.runBlocking

private val log = KotlinLogging.logger {}

/**
 * Slack implementation of [MetadataQuerier]. The streams are fixed ([SlackStream]) and have no
 * namespace; there is nothing to discover from the workspace. CHECK verifies the token with
 * `auth.test` and, like the legacy connector, reads the first page of `users.list`.
 *
 * During READ, [fields] are served from the configured catalog: the CDK validates every configured
 * stream against [fields] at start-up, and a catalog configured with an older schema (or the legacy
 * connector's) must keep loading.
 */
class SlackSourceMetadataQuerier(
    val configuration: SlackSourceConfiguration,
    private val client: SlackApiClient,
    private val configuredFields: Map<StreamIdentifier, List<EmittedField>> = emptyMap(),
) : MetadataQuerier {

    override fun streamNamespaces(): List<String> = emptyList()

    override fun streamNames(streamNamespace: String?): List<StreamIdentifier> =
        if (streamNamespace != null) emptyList() else SlackStream.entries.map { it.id }

    override fun fields(streamID: StreamIdentifier): List<EmittedField> =
        configuredFields[streamID]
            ?: SlackStream.byName(streamID.name)?.fields()
                ?: throw ConfigErrorException("Unknown stream '${streamID.name}'.")

    override fun primaryKey(streamID: StreamIdentifier): List<List<String>> =
        SlackStream.byName(streamID.name)?.primaryKey ?: emptyList()

    /** Token validity and the `users:read` scope, with Slack's own error names on failure. */
    override fun extraChecks() {
        runBlocking {
            val auth = client.get("auth.test")
            log.info {
                "Authenticated to Slack workspace '${auth.get("team")?.asText()}' " +
                    "(${auth.get("team_id")?.asText()}) as user ${auth.get("user_id")?.asText()}"
            }
            client.get("users.list", mapOf("limit" to "1"))
        }
    }

    override fun close() {
        client.close()
    }

    /** Slack implementation of [MetadataQuerier.Factory]. */
    @Singleton
    @Primary
    class Factory
    @Inject
    constructor(
        @Value("\${${Operation.PROPERTY}:discover}") private val operation: String = "discover",
        /** Empty for every operation but READ. */
        private val configuredCatalog: ConfiguredAirbyteCatalog = ConfiguredAirbyteCatalog(),
        @Value("\${${SlackSharedState.RATE_LIMIT_SCALE_PROPERTY}:1.0}")
        private val rateLimitScale: Double = 1.0,
    ) : MetadataQuerier.Factory<SlackSourceConfiguration> {
        override fun session(config: SlackSourceConfiguration): MetadataQuerier =
            SlackSourceMetadataQuerier(
                config,
                SlackApiClient(config, rateLimitScale),
                configuredFields =
                    if (operation == READ_OPERATION) fieldsFromConfiguredCatalog(configuredCatalog)
                    else emptyMap(),
            )
    }

    companion object {
        private const val READ_OPERATION = "read"

        /** The fields of each configured stream, from its own JSON schema. */
        fun fieldsFromConfiguredCatalog(
            configuredCatalog: ConfiguredAirbyteCatalog,
        ): Map<StreamIdentifier, List<EmittedField>> =
            configuredCatalog.streams.associate { configuredStream: ConfiguredAirbyteStream ->
                StreamIdentifier.from(configuredStream.stream) to
                    SlackStream.fieldsFromSchema(configuredStream.stream.jsonSchema)
            }
    }
}
