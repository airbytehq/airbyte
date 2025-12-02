/* Copyright (c) 2025 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.postgres.operations

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.NullNode
import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.command.OpaqueStateValue
import io.airbyte.cdk.data.JsonEncoder
import io.airbyte.cdk.discover.CdcOffsetDateTimeMetaFieldType
import io.airbyte.cdk.discover.CdcStringMetaFieldType
import io.airbyte.cdk.discover.CommonMetaField
import io.airbyte.cdk.discover.DataOrMetaField
import io.airbyte.cdk.discover.JdbcAirbyteStreamFactory
import io.airbyte.cdk.discover.MetaField
import io.airbyte.cdk.output.sockets.FieldValueEncoder
import io.airbyte.cdk.output.sockets.NativeRecordPayload
import io.airbyte.cdk.read.Stream
import io.airbyte.cdk.read.cdc.DebeziumOffset
import io.airbyte.integrations.source.postgres.cdc.PostgresSourceCdcMetaFields
import io.airbyte.integrations.source.postgres.cdc.PostgresSourceCdcPosition
import io.airbyte.integrations.source.postgres.cdc.PostgresSourceDebeziumOperations
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
        recordData.set<JsonNode>(
            PostgresSourceCdcMetaFields.CDC_LSN.id,
            // TODO: Duplicates CDC_LSN.type.
            //  Unable to use the reference due to * star projection.
            //  Note: the same is true in the MySQL connector.
            CdcStringMetaFieldType.jsonEncoder.encode(position.lsn.asString()),
        )
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
}
