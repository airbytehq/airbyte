/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.cdk.discover

import java.sql.JDBCType
import java.sql.Types

/** Supertype for all source database types. */
sealed interface SourceDatabaseType {
    val catalog: String?
    val schema: String?
    val typeName: String?
    val typeCode: Int
    val jdbcType: JDBCType?
        get() = JDBCType.entries.find { it.vendorTypeNumber == typeCode }
}

/** [SystemType] models types defined by the source database itself, i.e. no UDTs. */
data class SystemType(
    override val typeName: String? = null,
    override val typeCode: Int,
    val precision: Int? = null,
    val scale: Int? = null,
) : SourceDatabaseType {
    override val catalog: String?
        get() = null
    override val schema: String?
        get() = null
}

/**
 * Union type for all UDTs.
 *
 * Connectors may define additional implementations.
 *
 * The subtypes may overlap, for instance a user-defined array may be represented both as a
 * [UserDefinedArray] and as a [GenericUserDefinedType].
 */
interface UserDefinedType : SourceDatabaseType

/** User-defined array types. */
data class UserDefinedArray(
    override val catalog: String? = null,
    override val schema: String? = null,
    override val typeName: String,
    val elementType: SourceDatabaseType,
) : UserDefinedType {
    override val typeCode: Int
        get() = Types.ARRAY
}

/** Models a row for [java.sql.DatabaseMetaData.getUDTs]. */
data class GenericUserDefinedType(
    override val catalog: String? = null,
    override val schema: String? = null,
    override val typeName: String,
    override val typeCode: Int,
    val remarks: String? = null,
    val baseTypeCode: Int? = null,
) : UserDefinedType
