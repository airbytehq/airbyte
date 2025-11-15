package io.airbyte.integrations.destination.mysql.config

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.orchestration.db.ColumnNameGenerator
import io.airbyte.cdk.load.orchestration.db.FinalTableNameGenerator
import io.airbyte.cdk.load.orchestration.db.RawTableNameGenerator
import io.airbyte.cdk.load.table.TableName
import io.airbyte.integrations.destination.mysql.spec.MySQLConfiguration
import jakarta.inject.Singleton

@Singleton
class MySQLRawTableNameGenerator(
    private val config: MySQLConfiguration,
) : RawTableNameGenerator {
    override fun getTableName(streamDescriptor: DestinationStream.Descriptor): TableName {
        // Raw tables go to internal schema (usually not used in modern CDK)
        val namespace = config.database
        val name = "_airbyte_raw_${streamDescriptor.namespace}_${streamDescriptor.name}".toDbCompatible()
        return TableName(namespace, name)
    }
}

@Singleton
class MySQLFinalTableNameGenerator(
    private val config: MySQLConfiguration,
) : FinalTableNameGenerator {
    override fun getTableName(streamDescriptor: DestinationStream.Descriptor): TableName {
        val namespace = streamDescriptor.namespace?.toDbCompatible()
            ?: config.database
        val name = streamDescriptor.name.toDbCompatible()
        return TableName(namespace, name)
    }
}

@Singleton
class MySQLColumnNameGenerator : ColumnNameGenerator {
    override fun getColumnName(column: String): ColumnNameGenerator.ColumnName {
        val dbName = column.toDbCompatible()
        return ColumnNameGenerator.ColumnName(
            canonicalName = dbName,
            displayName = dbName,
        )
    }
}

// MySQL identifiers are case-insensitive by default (on case-insensitive file systems)
// but we'll preserve case for clarity
private fun String.toDbCompatible(): String {
    // For MySQL, we'll preserve the original case but sanitize special characters
    return this.replace("-", "_").replace(".", "_")
}
