package io.airbyte.integrations.source.mssql

import io.airbyte.cdk.StreamIdentifier
import io.airbyte.cdk.read.ConcurrencyResource
import io.airbyte.cdk.read.PartitionReader
import io.airbyte.cdk.read.StreamRecordConsumer
import io.airbyte.cdk.read.cdc.CdcPartitionReader
import io.airbyte.cdk.read.cdc.CdcPartitionReaderDebeziumOperations
import io.airbyte.cdk.read.cdc.DebeziumInput

class MsSqlServerCdcPartitionReader<T : Comparable<T>>(
    concurrencyResource: ConcurrencyResource,
    streamRecordConsumers: Map<StreamIdentifier, StreamRecordConsumer>,
    readerOps: CdcPartitionReaderDebeziumOperations<T>,
    upperBound: T,
    input: DebeziumInput,
    ): CdcPartitionReader<T>(concurrencyResource, streamRecordConsumers, readerOps, upperBound, input) {
}
