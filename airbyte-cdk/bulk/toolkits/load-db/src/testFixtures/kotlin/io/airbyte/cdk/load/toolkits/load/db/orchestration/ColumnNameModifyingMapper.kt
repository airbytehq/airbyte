/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.toolkits.load.db.orchestration

import io.airbyte.cdk.load.data.AirbyteType
import io.airbyte.cdk.load.data.ObjectValue
import io.airbyte.cdk.load.orchestration.db.ColumnNameGenerator
import io.airbyte.cdk.load.test.util.ExpectedRecordMapper
import io.airbyte.cdk.load.test.util.OutputRecord

class ColumnNameModifyingMapper(private val columnNameGenerator: ColumnNameGenerator) :
    ExpectedRecordMapper {
    override fun mapRecord(expectedRecord: OutputRecord, schema: AirbyteType): OutputRecord {
        val mappedProperties =
            expectedRecord.data.values.mapKeysTo(linkedMapOf()) { (k, _) ->
                columnNameGenerator.getColumnName(k).displayName
            }
        return expectedRecord.copy(data = ObjectValue(mappedProperties))
    }
}
