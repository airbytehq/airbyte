/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.slackv2

import io.airbyte.cdk.command.SourceConfiguration
import io.airbyte.cdk.discover.AirbyteStreamFactory
import io.airbyte.cdk.discover.DiscoveredStream
import io.airbyte.protocol.models.v0.AirbyteStream
import io.micronaut.context.annotation.Primary
import jakarta.inject.Singleton

/**
 * Builds each [AirbyteStream] exactly like the legacy connector's catalog: the legacy JSON schema
 * verbatim, `full_refresh` for users, channels and channel_members, `full_refresh` + `incremental`
 * with the source-defined cursor `float_ts` for channel_messages and threads, the legacy primary
 * keys, and `is_resumable` only for the incremental streams.
 */
@Singleton
@Primary
class SlackAirbyteStreamFactory : AirbyteStreamFactory {

    override fun create(
        config: SourceConfiguration,
        discoveredStream: DiscoveredStream
    ): AirbyteStream {
        val slackStream: SlackStream =
            SlackStream.byName(discoveredStream.id.name)
                ?: throw IllegalArgumentException("Unknown stream ${discoveredStream.id}")
        val stream: AirbyteStream =
            AirbyteStream()
                .withName(slackStream.streamName)
                .withJsonSchema(slackStream.jsonSchema())
                .withSupportedSyncModes(slackStream.supportedSyncModes)
                .withSourceDefinedPrimaryKey(slackStream.primaryKey)
                .withIsResumable(slackStream.incremental)
                .withIsFileBased(false)
        if (slackStream.incremental) {
            stream
                .withSourceDefinedCursor(true)
                .withDefaultCursorField(listOf(slackStream.cursorField))
        } else {
            // The model defaults to an empty list; the legacy catalog has no such key.
            stream.defaultCursorField = null
        }
        return stream
    }
}
