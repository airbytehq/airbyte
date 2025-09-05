/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres.operations.types

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.ObjectMapper
import com.fasterxml.jackson.databind.node.TextNode
import io.airbyte.cdk.data.JsonEncoder
import io.airbyte.cdk.data.LeafAirbyteSchemaType
import io.airbyte.cdk.jdbc.JdbcFieldType
import io.airbyte.cdk.jdbc.JdbcGetter
import java.sql.ResultSet

// In Postgres, hstore is like Map<String, String>. We output it as stringified json.
object HstoreFieldType :
    JdbcFieldType<Map<String, String?>>(
        LeafAirbyteSchemaType.STRING,
        HstoreGetter,
        HstoreEncoder,
    )

object HstoreGetter : JdbcGetter<Map<String, String?>> {
    override fun get(rs: ResultSet, colIdx: Int): Map<String, String?> {
        return rs.getString(colIdx)
            .split(",")
            .map { it.split("=>", limit = 2) } // split key => value
            .associate { parts ->
                val key = parts[0].trim().removeSurrounding("\"")
                val rawValue = parts[1].trim()
                val value = if (rawValue == "NULL") null else rawValue.removeSurrounding("\"")
                key to value
            }
    }
}

object HstoreEncoder : JsonEncoder<Map<String, String?>> {
    override fun encode(decoded: Map<String, String?>): JsonNode {
        return TextNode(nullValuePreservingObjectMapper.writeValueAsString(decoded))
    }
}

// Postgres HSTORE type supports mapping to null values.
// Our Jsons ObjectMapper class omits map entries with null values.
// This ObjectMapper includes them.
val nullValuePreservingObjectMapper: ObjectMapper = ObjectMapper()
