/* Copyright (c) 2025 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.postgres.operations

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.command.OpaqueStateValue
import io.airbyte.cdk.discover.CdcOffsetDateTimeMetaFieldType
import io.airbyte.cdk.discover.FieldOrMetaField
import io.airbyte.cdk.discover.JdbcAirbyteStreamFactory
import io.airbyte.cdk.discover.MetaField
import io.airbyte.cdk.read.Stream
import io.airbyte.integrations.source.postgres.PostgresSourceCdcMetaFields
import io.micronaut.context.annotation.Primary
import jakarta.inject.Singleton
import java.time.OffsetDateTime

@Singleton
@Primary
class PostgresSourceStreamFactory : JdbcAirbyteStreamFactory {

    override val globalCursor: FieldOrMetaField = PostgresSourceCdcMetaFields.CDC_LSN

    override val globalMetaFields: Set<MetaField> =
        setOf(
            PostgresSourceCdcMetaFields.CDC_LSN,
            PostgresSourceCdcMetaFields.UPDATED_AT,
            PostgresSourceCdcMetaFields.DELETED_AT,
        )

    override fun decorateRecordData(
        timestamp: OffsetDateTime,
        globalStateValue: OpaqueStateValue?,
        stream: Stream,
        recordData: ObjectNode
    ) {
        recordData.set<JsonNode>(
            PostgresSourceCdcMetaFields.UPDATED_AT.id,
            CdcOffsetDateTimeMetaFieldType.jsonEncoder.encode(timestamp),
        )
        recordData.set<JsonNode>(
            PostgresSourceCdcMetaFields.DELETED_AT.id,
            null,
        )

        // TODO: enable CDC
        /*if (globalStateValue == null) {
            return
        }
        val offset: DebeziumOffset =
            PostgresSourceDebeziumOperations.deserializeStateUnvalidated(globalStateValue).offset
        val position: PostgresSourceCdcPosition = PostgresSourceDebeziumOperations.position(offset)
        recordData.set<JsonNode>(
            PostgresSourceCdcMetaFields.CDC_LSN.id,
            CdcStringMetaFieldType.jsonEncoder.encode(position.lsn),
        )*/
    }
}
