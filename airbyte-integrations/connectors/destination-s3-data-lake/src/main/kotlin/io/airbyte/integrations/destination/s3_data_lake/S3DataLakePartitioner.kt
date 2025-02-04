/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3_data_lake

import io.airbyte.cdk.load.data.ObjectValue
import io.airbyte.cdk.load.message.DestinationRecordAirbyteValue
import io.airbyte.cdk.load.pipeline.InputPartitioner

/** This is just POC. Obviously we'd want the primary key. */
// Disabled because it started breaking things after rebase.
class S3DataLakePartitioner : InputPartitioner {
    override fun getPart(record: DestinationRecordAirbyteValue, numParts: Int): Int {
        val data = (record.data as ObjectValue)
        val source = (data.values["id"] ?: data.values.values.first()).toString()
        return source.hashCode() % numParts
    }
}
