package io.airbyte.cdk.load.writer.batch

import io.airbyte.cdk.load.message.DestinationRecordRaw

interface ResponseBodyBuilder {
    fun accumulate(record: DestinationRecordRaw)
    fun isEmpty(): Boolean
    fun isFull(): Boolean
    fun build(): ByteArray
}
