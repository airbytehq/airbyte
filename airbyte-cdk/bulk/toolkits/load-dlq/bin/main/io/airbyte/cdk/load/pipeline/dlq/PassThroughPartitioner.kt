/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.pipeline.dlq

import io.airbyte.cdk.load.message.DestinationRecordRaw
import io.airbyte.cdk.load.message.StreamKey
import io.airbyte.cdk.load.pipeline.OutputPartitioner

/** A partitioner that echoes the same partition as provided on the input. */
class PassThroughPartitioner :
    OutputPartitioner<StreamKey, DestinationRecordRaw, StreamKey, DlqStepOutput> {
    override fun getOutputKey(inputKey: StreamKey, output: DlqStepOutput): StreamKey = inputKey

    override fun getPart(outputKey: StreamKey, inputPart: Int, numParts: Int): Int = inputPart
}
