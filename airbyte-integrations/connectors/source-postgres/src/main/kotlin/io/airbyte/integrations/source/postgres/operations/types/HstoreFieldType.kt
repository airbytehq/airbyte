/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres.operations.types

import com.fasterxml.jackson.core.type.TypeReference
import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.ObjectMapper
import com.fasterxml.jackson.databind.node.TextNode
import io.airbyte.cdk.data.JsonCodec
import io.airbyte.cdk.data.LeafAirbyteSchemaType
import io.airbyte.cdk.jdbc.JdbcAccessor
import io.airbyte.cdk.jdbc.SymmetricJdbcFieldType
import java.sql.PreparedStatement
import java.sql.ResultSet

// In Postgres, hstore is like Map<String, String?>?. We output it as stringified json.
object HstoreFieldType :
    SymmetricJdbcFieldType<Map<String, String?>>(
        LeafAirbyteSchemaType.STRING,
        HstoreAccessor,
        HstoreCodec,
    )

object HstoreAccessor : JdbcAccessor<Map<String, String?>> {
    @Suppress("UNCHECKED_CAST")
    override fun get(rs: ResultSet, colIdx: Int): Map<String, String?>? {
        val obj = rs.getObject(colIdx) ?: return null
        return obj as Map<String, String?>
    }
    override fun set(stmt: PreparedStatement, paramIdx: Int, value: Map<String, String?>) {
        stmt.setString(
            paramIdx,
            value
                .map {
                    if (it.value == null) {
                        "'${it.key}',NULL"
                    } else {
                        "'${it.key}','${it.value}'"
                    }
                }
                .joinToString(",", prefix = "hstore(", postfix = ")")
        )
    }
}

object HstoreCodec : JsonCodec<Map<String, String?>> {
    override fun encode(decoded: Map<String, String?>): JsonNode {
        return TextNode(nullValuePreservingObjectMapper.writeValueAsString(decoded))
    }

    override fun decode(encoded: JsonNode): Map<String, String?> {
        return nullValuePreservingObjectMapper.readValue(
            encoded.asText(),
            object : TypeReference<Map<String, String?>>() {}
        )
    }
}

// Postgres HSTORE type supports mapping to null values.
// Our Jsons ObjectMapper class omits map entries with null values.
// This ObjectMapper includes them.
val nullValuePreservingObjectMapper: ObjectMapper = ObjectMapper()
