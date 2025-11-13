/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

import io.airbyte.cdk.load.data.AirbyteValueProxy
import io.airbyte.cdk.load.data.IntegerType
import io.airbyte.cdk.load.integrationTest.DlqStateFactory
import io.airbyte.cdk.load.integrationTest.DlqTestState
import io.airbyte.cdk.load.message.DestinationRecordRaw
import io.airbyte.cdk.load.message.StreamKey
import io.airbyte.cdk.load.message.dlq.toDlqRecord
import java.math.BigInteger
import java.util.UUID

class DlqStateWithNewRecords : DlqTestState {
    private val records: MutableList<DestinationRecordRaw> = mutableListOf()

    override fun accumulate(record: DestinationRecordRaw) {
        records.add(record)
    }

    override fun isFull(): Boolean = records.size > 2

    override fun flush(): List<DestinationRecordRaw>? =
        records
            .filter { it.hasAnEvenId() }
            .map {
                it.toDlqRecord(
                    mapOf(
                        "error" to UUID.randomUUID(),
                        "message" to "very custom error message",
                    )
                )
            }
            .ifEmpty { null }

    override fun close() {}

    // Just so that we do not write everything to the dead letter queue
    // we only write even ids that are less than 10
    private fun DestinationRecordRaw.hasAnEvenId(): Boolean {
        val id =
            this.rawData
                .asAirbyteValueProxy()
                .getInteger(AirbyteValueProxy.FieldAccessor(0, "id", IntegerType))
        return id?.let { it < BigInteger.TEN && it.mod(BigInteger.TWO) == BigInteger.ZERO } ?: true
    }

    class Factory : DlqStateFactory {
        override fun create(key: StreamKey, part: Int): DlqTestState = DlqStateWithNewRecords()
    }
}
