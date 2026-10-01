/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.dataflow.pipeline

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.dataflow.aggregate.Aggregate
import io.airbyte.cdk.load.dataflow.state.PartitionHistogram
import io.airbyte.cdk.load.dataflow.state.PartitionKey
import io.airbyte.cdk.load.dataflow.transform.RecordDTO
import io.airbyte.cdk.load.message.ArrowBatchDTO
import io.airbyte.cdk.load.message.DestinationArrowBatch
import io.airbyte.cdk.load.message.DestinationRecordRaw

data class DataFlowStageIO(
    var raw: DestinationRecordRaw? = null,
    var arrowBatch: DestinationArrowBatch? = null,
    var partitionKey: PartitionKey? = null,
    var munged: RecordDTO? = null,
    var parsedArrowBatch: ArrowBatchDTO? = null,
    var aggregate: Aggregate? = null,
    var partitionCountsHistogram: PartitionHistogram? = null,
    var partitionBytesHistogram: PartitionHistogram? = null,
    var mappedDesc: DestinationStream.Descriptor? = null,
)
