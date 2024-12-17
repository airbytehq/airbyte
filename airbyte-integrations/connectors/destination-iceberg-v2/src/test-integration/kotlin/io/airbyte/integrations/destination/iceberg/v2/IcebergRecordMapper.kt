/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.iceberg.v2

import io.airbyte.cdk.load.data.AirbyteType
import io.airbyte.cdk.load.data.ObjectValue
import io.airbyte.cdk.load.data.SchemalessValuesToJsonString
import io.airbyte.cdk.load.test.util.ExpectedRecordMapper
import io.airbyte.cdk.load.test.util.OutputRecord

object IcebergRecordMapper : ExpectedRecordMapper {
    override fun mapRecord(expectedRecord: OutputRecord, schema: AirbyteType): OutputRecord {
        val (mappedData, _) = SchemalessValuesToJsonString().map(expectedRecord.data, schema)
        return expectedRecord.copy(data = mappedData as ObjectValue)
    }
}
