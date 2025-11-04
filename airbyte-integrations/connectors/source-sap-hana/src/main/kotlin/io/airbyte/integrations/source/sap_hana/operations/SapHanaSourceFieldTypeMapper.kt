/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.sap_hana.operations

import io.airbyte.cdk.discover.FieldType
import io.airbyte.cdk.discover.JdbcMetadataQuerier
import io.airbyte.cdk.discover.SystemType
import io.airbyte.cdk.jdbc.*
import io.micronaut.context.annotation.Primary
import jakarta.inject.Singleton
import java.sql.Types

@Singleton
@Primary
class SapHanaSourceFieldTypeMapper : JdbcMetadataQuerier.FieldTypeMapper {

    override fun toFieldType(c: JdbcMetadataQuerier.ColumnMetadata): FieldType {
        if (c.type.typeCode == Types.ARRAY) {
            return SapHanaArrayFieldType(leafType(parseArrayElementType(c.type.typeName)))
        }
        return when (val type = c.type) {
            is SystemType -> leafType(type.typeName)
            else -> PokemonFieldType
        }
    }

    private fun parseArrayElementType(typeName: String?): String? {
        return when {
            // SAP HANA returns the array type as "ARRAY" appended to the base type name e.g.
            // "INTEGER ARRAY"
            typeName != null && " ARRAY" in typeName -> typeName.substringBefore(" ARRAY")
            else ->
                throw RuntimeException("Cannot parse array element type from type name: $typeName")
        }
    }

    private fun leafType(typeName: String?): JdbcFieldType<*> {
        return when (typeName) {
            "BOOLEAN" -> BooleanFieldType
            "TINYINT",
            "SMALLINT", -> ShortFieldType
            "DOUBLE" -> DoubleFieldType
            "FLOAT",
            "REAL",
            "SMALLDECIMAL",
            "DECIMAL",
            "DEC", -> BigDecimalFieldType
            "INTEGER" -> IntFieldType
            "BIGINT" -> BigIntegerFieldType
            "CHAR",
            "VARCHAR",
            "ALPHANUM", -> StringFieldType
            "NCHAR",
            "NVARCHAR",
            "SHORTTEXT", -> NStringFieldType
            "BINARY",
            "VARBINARY",
            "REAL_VECTOR", -> BinaryStreamFieldType
            "TIME" -> LocalTimeFieldType
            "DATE" -> LocalDateFieldType
            "SECONDDATE",
            "TIMESTAMP", -> LocalDateTimeFieldType
            "BLOB" -> BinaryStreamFieldType
            "CLOB" -> ClobFieldType
            "NCLOB",
            "TEXT",
            "BINTEXT", -> NClobFieldType
            "ST_POINT",
            "ST_GEOMETRY", -> BinaryStreamFieldType
            else -> PokemonFieldType
        }
    }
}
