/* Copyright (c) 2025 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.db2.operations

import io.airbyte.cdk.discover.FieldType
import io.airbyte.cdk.discover.JdbcMetadataQuerier
import io.airbyte.cdk.discover.SystemType
import io.airbyte.cdk.jdbc.*
import io.micronaut.context.annotation.Primary
import jakarta.inject.Singleton

@Singleton
@Primary
class Db2SourceFieldTypeMapper : JdbcMetadataQuerier.FieldTypeMapper {

    override fun toFieldType(c: JdbcMetadataQuerier.ColumnMetadata): FieldType {
        return when (val type = c.type) {
            is SystemType -> leafType(type.typeName, type.scale != null && type.scale != 0)
            else -> PokemonFieldType
        }
    }

    private fun leafType(
        typeName: String?,
        notInteger: Boolean,
    ): JdbcFieldType<*> =
        when (typeName) {

            // TODO: extract ANSI defaults

            // Numeric types
            "SMALLINT" -> ShortFieldType
            "INTEGER",
            "INT" -> IntFieldType
            "BIGINT" -> BigIntegerFieldType
            "DECIMAL",
            "DEC",
            "NUMERIC" -> if (notInteger) BigDecimalFieldType else BigIntegerFieldType
            "REAL",
            "FLOAT" -> FloatFieldType
            "DOUBLE",
            "DOUBLE PRECISION" -> DoubleFieldType
            "DECFLOAT" -> BigDecimalFieldType

            // String types
            "CHAR",
            "CHARACTER" -> StringFieldType
            "VARCHAR",
            "CHARACTER VARYING",
            "CHAR VARYING" -> StringFieldType
            "CLOB",
            "CHARACTER LARGE OBJECT",
            "CHAR LARGE OBJECT" -> ClobFieldType
            "DBCLOB" -> NClobFieldType

            // Graphic string types
            "GRAPHIC" -> NStringFieldType
            "VARGRAPHIC" -> NStringFieldType

            // Binary types
            "BLOB",
            "BINARY LARGE OBJECT" -> BinaryStreamFieldType
            "BINARY" -> BinaryStreamFieldType
            "VARBINARY",
            "BINARY VARYING" -> BinaryStreamFieldType

            // Date/time types
            "DATE" -> LocalDateFieldType
            "TIME" -> LocalTimeFieldType
            "TIMESTAMP" -> LocalDateTimeFieldType

            // Boolean type
            "BOOLEAN" -> BooleanFieldType

            // Special types
            "XML" -> XmlFieldType
            // TODO: support ROWID for non-LUW installations
            // "ROWID" -> StringFieldType

            // Default case
            else -> PokemonFieldType
        }
}
