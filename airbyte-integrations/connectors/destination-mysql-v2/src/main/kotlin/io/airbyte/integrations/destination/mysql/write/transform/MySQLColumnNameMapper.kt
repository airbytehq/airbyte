package io.airbyte.integrations.destination.mysql.write.transform

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.dataflow.transform.ColumnNameMapper
import io.airbyte.cdk.load.orchestration.db.legacy_typing_deduping.TableCatalog
import jakarta.inject.Singleton

@Singleton
class MySQLColumnNameMapper(
    private val names: TableCatalog,
) : ColumnNameMapper {
    override fun getMappedColumnName(
        stream: DestinationStream,
        columnName: String
    ): String? {
        return names[stream]?.columnNameMapping?.get(columnName)
    }
}
