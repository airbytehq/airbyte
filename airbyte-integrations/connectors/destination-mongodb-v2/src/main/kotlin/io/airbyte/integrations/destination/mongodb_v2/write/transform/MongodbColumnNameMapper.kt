/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mongodb_v2.write.transform

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.dataflow.transform.ColumnNameMapper
import io.airbyte.cdk.load.orchestration.db.legacy_typing_deduping.TableCatalog
import jakarta.inject.Singleton

@Singleton
class MongodbColumnNameMapper(
    private val names: TableCatalog,
) : ColumnNameMapper {
    override fun getMappedColumnName(
        stream: DestinationStream,
        columnName: String
    ): String? {
        return names[stream]?.columnNameMapping?.get(columnName)
    }
}
