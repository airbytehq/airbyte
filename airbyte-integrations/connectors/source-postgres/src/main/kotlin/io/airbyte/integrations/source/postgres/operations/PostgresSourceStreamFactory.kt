/* Copyright (c) 2025 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.postgres.operations

import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.command.OpaqueStateValue
import io.airbyte.cdk.command.SourceConfiguration
import io.airbyte.cdk.discover.AirbyteStreamFactory
import io.airbyte.cdk.discover.DataOrMetaField
import io.airbyte.cdk.discover.DiscoveredStream
import io.airbyte.cdk.discover.JdbcAirbyteStreamFactory
import io.airbyte.cdk.discover.MetaField
import io.airbyte.cdk.output.sockets.NativeRecordPayload
import io.airbyte.cdk.read.Stream
import io.airbyte.integrations.source.postgres.PostgresSourceCdcMetaFields
import io.airbyte.integrations.source.postgres.config.PostgresSourceConfiguration
import io.airbyte.integrations.source.postgres.config.XminIncrementalConfiguration
import io.airbyte.protocol.models.v0.AirbyteStream
import io.airbyte.protocol.models.v0.SyncMode
import io.micronaut.context.annotation.Primary
import jakarta.inject.Singleton
import java.time.OffsetDateTime

@Singleton
@Primary
class PostgresSourceStreamFactory : JdbcAirbyteStreamFactory {

    override val globalCursor: DataOrMetaField = PostgresSourceCdcMetaFields.CDC_CURSOR

    override val globalMetaFields: Set<MetaField> = emptySet() // TEMP

    override fun decorateRecordData(
        timestamp: OffsetDateTime,
        globalStateValue: OpaqueStateValue?,
        stream: Stream,
        recordData: ObjectNode
    ) {
        TODO()
    }

    override fun decorateRecordData(
        timestamp: OffsetDateTime,
        globalStateValue: OpaqueStateValue?,
        stream: Stream,
        recordData: NativeRecordPayload
    ) {
        TODO()
    }

    override fun create(
        config: SourceConfiguration,
        discoveredStream: DiscoveredStream
    ): AirbyteStream {
        val postgresConfig = config as PostgresSourceConfiguration
        val isCdc = config.isCdc()
        val hasPK = hasValidPrimaryKey(discoveredStream)
        val hasPotentialCursorField = hasPotentialCursorFields(discoveredStream)

        val isXmin = postgresConfig.incrementalConfiguration is XminIncrementalConfiguration
        val syncModes =
            when {
                // Incremental sync is only provided as a sync option if the stream has a potential
                // cursor field or is configured as CDC with a valid primary key.
                !isCdc && hasPotentialCursorField || (isCdc || isXmin) && hasPK ->
                    listOf(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL)
                else -> listOf(SyncMode.FULL_REFRESH)
            }
        val primaryKey: List<List<String>> =
            if (isCdc || hasPK) discoveredStream.primaryKeyColumnIDs else emptyList()
        val stream =
            AirbyteStreamFactory.createAirbyteStream(discoveredStream).apply {
                if (isCdc && hasPK) {
                    decorateAirbyteStream(this)
                }
                supportedSyncModes = syncModes
                sourceDefinedPrimaryKey = primaryKey
                sourceDefinedCursor = (isCdc || isXmin) && hasPK
                isResumable = hasPK
            }
        return stream
    }
}
