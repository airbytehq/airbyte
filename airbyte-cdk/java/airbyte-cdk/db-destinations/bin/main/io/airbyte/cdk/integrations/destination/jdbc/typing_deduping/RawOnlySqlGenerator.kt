/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.destination.jdbc.typing_deduping

import io.airbyte.cdk.integrations.destination.NamingConventionTransformer
import io.airbyte.integrations.base.destination.typing_deduping.AirbyteType
import io.airbyte.integrations.base.destination.typing_deduping.ColumnId
import java.util.*
import org.jooq.Condition
import org.jooq.DataType
import org.jooq.Field
import org.jooq.SQLDialect

/**
 * Some Destinations do not support Typing and Deduping but have the updated raw table format
 * SqlGenerator implementations are only for "final" tables and are a required input for
 * TyperDeduper classes. This implementation appeases that requirement but does not implement any
 * "final" table operations.
 */
open class RawOnlySqlGenerator(namingTransformer: NamingConventionTransformer) :
    JdbcSqlGenerator(namingTransformer) {
    override val structType: DataType<*>
        get() {
            throw NotImplementedError("This Destination does not support final tables")
        }

    override val arrayType: DataType<*>
        get() {
            throw NotImplementedError("This Destination does not support final tables")
        }

    override val widestType: DataType<*>
        get() {
            throw NotImplementedError("This Destination does not support final tables")
        }

    override val dialect: SQLDialect
        get() {
            throw NotImplementedError("This Destination does not support final tables")
        }

    override fun extractRawDataFields(
        columns: LinkedHashMap<ColumnId, AirbyteType>,
        useExpensiveSaferCasting: Boolean,
    ): MutableList<Field<*>> {
        throw NotImplementedError("This Destination does not support final tables")
    }

    override fun buildAirbyteMetaColumn(columns: LinkedHashMap<ColumnId, AirbyteType>): Field<*> {
        throw NotImplementedError("This Destination does not support final tables")
    }

    override fun cdcDeletedAtNotNullCondition(): Condition {
        throw NotImplementedError("This Destination does not support final tables")
    }

    override fun getRowNumber(
        primaryKey: List<ColumnId>,
        cursorField: Optional<ColumnId>,
    ): Field<Int> {
        throw NotImplementedError("This Destination does not support final tables")
    }
}
