package io.airbyte.cdk.integrations.destination.jdbc.typing_deduping

import io.airbyte.cdk.integrations.destination.NamingConventionTransformer
import io.airbyte.cdk.integrations.destination.jdbc.TableDefinition
import io.airbyte.integrations.base.destination.typing_deduping.AirbyteType
import io.airbyte.integrations.base.destination.typing_deduping.ColumnId
import io.airbyte.integrations.base.destination.typing_deduping.StreamConfig
import org.jooq.Condition
import org.jooq.DataType
import org.jooq.Field
import org.jooq.SQLDialect
import java.util.*

/**
 * Some Destinations do not support Typing and Deduping but have the updated raw table format
 * SqlGenerator implementations are only for "final" tables and are a required input for
 * TyperDeduper classes. This implementation appeases that requirement but does not implement
 * any "final" table operations.
 */
class RawOnlySqlGenerator(private val namingTransformer: NamingConventionTransformer) :
    JdbcSqlGenerator(namingTransformer) {
    override fun getStructType(): DataType<*>? {
        throw NotImplementedError("This Destination does not support final tables")
    }

    override fun getArrayType(): DataType<*>? {
        throw NotImplementedError("This Destination does not support final tables")
    }

    override fun getWidestType(): DataType<*>? {
        throw NotImplementedError("This Destination does not support final tables")
    }

    override fun getDialect(): SQLDialect? {
        throw NotImplementedError("This Destination does not support final tables")
    }

    override fun extractRawDataFields(
        columns: LinkedHashMap<ColumnId, AirbyteType>,
        useExpensiveSaferCasting: Boolean
    ): List<Field<*>>? {
        throw NotImplementedError("This Destination does not support final tables")
    }

    override fun buildAirbyteMetaColumn(columns: LinkedHashMap<ColumnId, AirbyteType>): Field<*>? {
        throw NotImplementedError("This Destination does not support final tables")
    }

    override fun cdcDeletedAtNotNullCondition(): Condition? {
        throw NotImplementedError("This Destination does not support final tables")
    }

    override fun getRowNumber(
        primaryKey: List<ColumnId>,
        cursorField: Optional<ColumnId>
    ): Field<Int>? {
        throw NotImplementedError("This Destination does not support final tables")
    }

    override fun existingSchemaMatchesStreamConfig(
        stream: StreamConfig,
        existingTable: TableDefinition
    ): Boolean {
        throw NotImplementedError("This Destination does not support final tables")
    }
}
