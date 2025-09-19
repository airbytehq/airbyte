/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres

import io.airbyte.cdk.command.OpaqueStateValue
import io.airbyte.cdk.read.Stream
import io.airbyte.cdk.read.cdc.CdcPartitionReaderDebeziumOperations
import io.airbyte.cdk.read.cdc.CdcPartitionsCreatorDebeziumOperations
import io.airbyte.cdk.read.cdc.DebeziumOffset
import io.airbyte.cdk.read.cdc.DebeziumRecordKey
import io.airbyte.cdk.read.cdc.DebeziumRecordValue
import io.airbyte.cdk.read.cdc.DebeziumSchemaHistory
import io.airbyte.cdk.read.cdc.DebeziumWarmStartState
import io.airbyte.cdk.read.cdc.DeserializedRecord
import jakarta.inject.Singleton
import org.apache.kafka.connect.source.SourceRecord

@Singleton
class PostgresSourceDebeziumOperations :
    CdcPartitionsCreatorDebeziumOperations<PostgresSourceCdcPosition>,
    CdcPartitionReaderDebeziumOperations<PostgresSourceCdcPosition> {
    override fun position(offset: DebeziumOffset): PostgresSourceCdcPosition {
        TODO("Not yet implemented")
    }

    override fun generateColdStartOffset(): DebeziumOffset {
        TODO("Not yet implemented")
    }

    override fun generateColdStartProperties(streams: List<Stream>): Map<String, String> {
        TODO("Not yet implemented")
    }

    override fun deserializeState(opaqueStateValue: OpaqueStateValue): DebeziumWarmStartState {
        TODO("Not yet implemented")
    }

    override fun generateWarmStartProperties(streams: List<Stream>): Map<String, String> {
        TODO("Not yet implemented")
    }

    override fun deserializeRecord(
        key: DebeziumRecordKey,
        value: DebeziumRecordValue,
        stream: Stream
    ): DeserializedRecord? {
        TODO("Not yet implemented")
    }

    override fun findStreamNamespace(key: DebeziumRecordKey, value: DebeziumRecordValue): String? {
        TODO("Not yet implemented")
    }

    override fun findStreamName(key: DebeziumRecordKey, value: DebeziumRecordValue): String? {
        TODO("Not yet implemented")
    }

    override fun serializeState(
        offset: DebeziumOffset,
        schemaHistory: DebeziumSchemaHistory?
    ): OpaqueStateValue {
        TODO("Not yet implemented")
    }

    override fun position(recordValue: DebeziumRecordValue): PostgresSourceCdcPosition? {
        TODO("Not yet implemented")
    }

    override fun position(sourceRecord: SourceRecord): PostgresSourceCdcPosition? {
        TODO("Not yet implemented")
    }
}
