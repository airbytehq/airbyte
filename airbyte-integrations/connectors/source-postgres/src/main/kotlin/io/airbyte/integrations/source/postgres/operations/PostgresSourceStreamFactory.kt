/* Copyright (c) 2025 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.postgres.operations

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.NullNode
import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.command.OpaqueStateValue
import io.airbyte.cdk.command.SourceConfiguration
import io.airbyte.cdk.data.JsonEncoder
import io.airbyte.cdk.discover.AirbyteStreamFactory
import io.airbyte.cdk.discover.CdcOffsetDateTimeMetaFieldType
import io.airbyte.cdk.discover.CdcStringMetaFieldType
import io.airbyte.cdk.discover.CommonMetaField
import io.airbyte.cdk.discover.DataOrMetaField
import io.airbyte.cdk.discover.DiscoveredStream
import io.airbyte.cdk.discover.JdbcAirbyteStreamFactory
import io.airbyte.cdk.discover.MetaField
import io.airbyte.cdk.output.sockets.FieldValueEncoder
import io.airbyte.cdk.output.sockets.NativeRecordPayload
import io.airbyte.cdk.read.Stream
import io.airbyte.cdk.read.cdc.DebeziumOffset
import io.airbyte.integrations.source.postgres.cdc.PostgresSourceCdcMetaFields
import io.airbyte.integrations.source.postgres.cdc.PostgresSourceCdcPosition
import io.airbyte.integrations.source.postgres.cdc.PostgresSourceDebeziumOperations
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

    override val globalCursor: DataOrMetaField = PostgresSourceCdcMetaFields.CDC_LSN

    override val globalMetaFields: Set<MetaField> =
        setOf(
            PostgresSourceCdcMetaFields.CDC_LSN,
            CommonMetaField.CDC_UPDATED_AT,
            CommonMetaField.CDC_DELETED_AT,
        )

    override fun decorateRecordData(
        timestamp: OffsetDateTime,
        globalStateValue: OpaqueStateValue?,
        stream: Stream,
        recordData: ObjectNode
    ) {
        recordData.set<JsonNode>(
            CommonMetaField.CDC_UPDATED_AT.id,
            CdcOffsetDateTimeMetaFieldType.jsonEncoder.encode(timestamp),
        )
        recordData.set<JsonNode>(PostgresSourceCdcMetaFields.CDC_LSN.id, NullNode.getInstance())
        if (globalStateValue == null) {
            return
        }
        val offset: DebeziumOffset =
            PostgresSourceDebeziumOperations.deserializeStateUnvalidated(globalStateValue)
        val position: PostgresSourceCdcPosition = PostgresSourceDebeziumOperations.position(offset)
        val lsn = position.lsn?.asString()
        if (lsn != null) {
            recordData.set<JsonNode>(
                PostgresSourceCdcMetaFields.CDC_LSN.id,
                // TODO: Duplicates CDC_LSN.type.
                //  Unable to use the reference due to * star projection.
                //  Note: the same is true in the MySQL connector.
                CdcStringMetaFieldType.jsonEncoder.encode(lsn),
            )
        }
    }

    @Suppress("UNCHECKED_CAST")
    override fun decorateRecordData(
        timestamp: OffsetDateTime,
        globalStateValue: OpaqueStateValue?,
        stream: Stream,
        recordData: NativeRecordPayload
    ) {
        recordData[CommonMetaField.CDC_UPDATED_AT.id] =
            FieldValueEncoder(
                timestamp,
                CommonMetaField.CDC_UPDATED_AT.type.jsonEncoder as JsonEncoder<Any>
            )
        recordData[PostgresSourceCdcMetaFields.CDC_LSN.id] =
            FieldValueEncoder(
                0.toDouble(),
                PostgresSourceCdcMetaFields.CDC_LSN.type.jsonEncoder as JsonEncoder<Any>
            )
        if (globalStateValue == null) {
            return
        }
        val offset: DebeziumOffset =
            PostgresSourceDebeziumOperations.deserializeStateUnvalidated(globalStateValue)
        val position: PostgresSourceCdcPosition = PostgresSourceDebeziumOperations.position(offset)
        recordData[PostgresSourceCdcMetaFields.CDC_LSN.id] =
            FieldValueEncoder(
                position.lsn,
                PostgresSourceCdcMetaFields.CDC_LSN.type.jsonEncoder as JsonEncoder<Any>
            )
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
                // cursor field or is configured as CDC or Xmin with a valid primary key.
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
