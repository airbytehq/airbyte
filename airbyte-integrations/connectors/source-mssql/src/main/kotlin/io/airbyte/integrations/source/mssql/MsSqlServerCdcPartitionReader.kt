package io.airbyte.integrations.source.mssql

import io.airbyte.cdk.StreamIdentifier
import io.airbyte.cdk.read.ConcurrencyResource
import io.airbyte.cdk.read.PartitionReader
import io.airbyte.cdk.read.StreamRecordConsumer
import io.airbyte.cdk.read.cdc.*

class MsSqlServerCdcPartitionReader<T : Comparable<T>>(
    concurrencyResource: ConcurrencyResource,
    streamRecordConsumers: Map<StreamIdentifier, StreamRecordConsumer>,
    readerOps: CdcPartitionReaderDebeziumOperations<T>,
    upperBound: T,
    debeziumProperties: Map<String, String>,
    startingOffset: DebeziumOffset,
    startingSchemaHistory: DebeziumSchemaHistory?,
    isInputStateSynthetic: Boolean,
    ): CdcPartitionReader<T>(concurrencyResource, streamRecordConsumers, readerOps, upperBound, debeziumProperties,
    startingOffset,
    startingSchemaHistory,
    isInputStateSynthetic) {
}
