/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.databricksv2.write.load

import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.schema.model.TableName
import io.airbyte.integrations.destination.databricksv2.sql.DatabricksSqlGenerator
import javax.sql.DataSource

class DatabricksInsertBuffer(
    private val tableName: TableName,
    val columns: List<String>,
    private val dataSource: DataSource,
    private val sqlGenerator: DatabricksSqlGenerator,
) {

    fun accumulate(recordFields: Map<String, AirbyteValue>) {
        TODO("Implement record accumulation into in-memory buffer")
    }

    suspend fun flush() {
        TODO("Implement flush")
    }
}
