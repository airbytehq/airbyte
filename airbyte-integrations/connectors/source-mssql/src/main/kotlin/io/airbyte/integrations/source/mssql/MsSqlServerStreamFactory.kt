/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mssql

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.command.OpaqueStateValue
import io.airbyte.cdk.discover.*
import io.airbyte.cdk.read.Stream
import io.micronaut.context.annotation.Primary
import jakarta.inject.Singleton
import java.time.OffsetDateTime

@Singleton
@Primary
class MsSqlServerStreamFactory : JdbcAirbyteStreamFactory {
    override val globalCursor: MetaField? = null
    override val globalMetaFields: Set<MetaField> =
        setOf(
            CommonMetaField.CDC_UPDATED_AT,
            CommonMetaField.CDC_DELETED_AT,
            MsSqlServerCdcMetaFields.CDC_CURSOR,
            MsSqlServerCdcMetaFields.CDC_EVENT_SERIAL_NO,
            MsSqlServerCdcMetaFields.CDC_LSN,
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
        ) /*
          recordData.set<JsonNode>(
              MsSqlServerCdcMetaFields.CDC_EVENT_SERIAL_NO.id,
              CdcIntegerMetaFieldType.jsonEncoder.encode(1),
          )
          recordData.set<JsonNode>(
              MysqlCdcMetaFields.CDC_LOG_POS.id,
              CdcIntegerMetaFieldType.jsonEncoder.encode(0),
          )
          if (globalStateValue == null) {
              return
          }
          val debeziumState: DebeziumState =
              MySqlDebeziumOperations.deserializeDebeziumState(globalStateValue)
          val position: MySqlPosition = MySqlDebeziumOperations.position(debeziumState.offset)
          recordData.set<JsonNode>(
              MysqlCdcMetaFields.CDC_LOG_FILE.id,
              CdcStringMetaFieldType.jsonEncoder.encode(position.fileName),
          )
          recordData.set<JsonNode>(
              MysqlCdcMetaFields.CDC_LOG_POS.id,
              CdcIntegerMetaFieldType.jsonEncoder.encode(position.position),
          )*/
    }

    enum class MsSqlServerCdcMetaFields(
        override val type: FieldType,
    ) : MetaField {
        CDC_CURSOR(CdcIntegerMetaFieldType),
        CDC_LSN(CdcIntegerMetaFieldType),
        CDC_EVENT_SERIAL_NO(CdcStringMetaFieldType),
        ;

        override val id: String
            get() = MetaField.META_PREFIX + name.lowercase()
    }
}
