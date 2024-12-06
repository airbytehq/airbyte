/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mssql

import io.airbyte.cdk.command.OpaqueStateValue
import io.airbyte.cdk.read.Stream
import io.airbyte.cdk.read.cdc.*
import io.airbyte.cdk.util.Jsons
import jakarta.inject.Singleton
import org.apache.kafka.connect.source.SourceRecord

@Singleton
class MsSqlServerDebeziumOperations : DebeziumOperations<MsSqlServerDebeziumPosition> {
    override fun position(offset: DebeziumOffset): MsSqlServerDebeziumPosition {
        return MsSqlServerDebeziumPosition()
    }

    override fun position(recordValue: DebeziumRecordValue): MsSqlServerDebeziumPosition? {
        return MsSqlServerDebeziumPosition()
    }

    override fun position(sourceRecord: SourceRecord): MsSqlServerDebeziumPosition? {
        return MsSqlServerDebeziumPosition()
    }

    override fun synthesize(): DebeziumInput {
        return DebeziumInput(
            isSynthetic = true,
            state = DebeziumState(DebeziumOffset(emptyMap()), null),
            properties = emptyMap()
        )
    }

    override fun deserialize(
        opaqueStateValue: OpaqueStateValue,
        streams: List<Stream>
    ): DebeziumInput {
        return DebeziumInput(
            isSynthetic = true,
            state = DebeziumState(DebeziumOffset(emptyMap()), null),
            properties = emptyMap()
        )
    }

    override fun deserialize(
        key: DebeziumRecordKey,
        value: DebeziumRecordValue,
        stream: Stream,
    ): DeserializedRecord? {
        return null
    }

    override fun findStreamNamespace(key: DebeziumRecordKey, value: DebeziumRecordValue): String? {
        return null
    }

    override fun findStreamName(key: DebeziumRecordKey, value: DebeziumRecordValue): String? {
        return null
    }

    override fun serialize(debeziumState: DebeziumState): OpaqueStateValue {
        return Jsons.objectNode()
    }
}

class MsSqlServerDebeziumPosition : Comparable<MsSqlServerDebeziumPosition> {
    override fun compareTo(other: MsSqlServerDebeziumPosition): Int {
        return 0
    }
}
