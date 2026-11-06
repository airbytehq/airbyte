/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres.operations.types

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.data.JsonCodec
import io.airbyte.cdk.data.LeafAirbyteSchemaType
import io.airbyte.cdk.jdbc.JdbcFieldType
import io.airbyte.cdk.jdbc.JdbcGetter
import io.airbyte.cdk.util.Jsons
import java.sql.ResultSet

// Field type for Postgres types that must be read via rs.getObject() to get the JDBC driver's
// Java object representation (e.g. PGpoint, PGbox), whose toString() produces the correctly
// formatted string (e.g. "(3.0,7.0)"). rs.getString() would give the compact form "(3,7)".
object AnyFieldType :
    JdbcFieldType<String>(
        LeafAirbyteSchemaType.STRING,
        PgObjectStringAccessor,
        PgObjectStringCodec,
    )

private object PgObjectStringAccessor : JdbcGetter<String> {
    override fun get(rs: ResultSet, colIdx: Int): String? =
        rs.getObject(colIdx)?.takeUnless { rs.wasNull() }?.toString()
}

private object PgObjectStringCodec : JsonCodec<String> {
    override fun encode(decoded: String): JsonNode = Jsons.textNode(decoded)

    // Use asText() so this works whether the node is a TextNode or any other type
    // (e.g. if Debezium or a future path sends a non-string node).
    override fun decode(encoded: JsonNode): String = encoded.asText()
}
