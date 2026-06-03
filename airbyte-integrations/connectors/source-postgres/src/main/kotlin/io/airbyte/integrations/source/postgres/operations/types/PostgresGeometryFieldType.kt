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

// Field type for PostGIS geometry/geography columns. The JDBC driver returns these as a
// hex-encoded EWKB string via rs.getString(); we normalize to canonical EWKT
// (e.g. "SRID=4326;POINT(11.5 48.1)") so the snapshot path matches what the CDC custom converter
// emits. See PostgisGeometry and PostgresCustomConverter.registerGeometry.
object PostgresGeometryFieldType :
    JdbcFieldType<String>(
        LeafAirbyteSchemaType.STRING,
        PgGeometryStringAccessor,
        PgGeometryStringCodec,
    )

private object PgGeometryStringAccessor : JdbcGetter<String> {
    override fun get(rs: ResultSet, colIdx: Int): String? =
        PostgisGeometry.toEwkt(rs.getString(colIdx)?.takeUnless { rs.wasNull() })
}

private object PgGeometryStringCodec : JsonCodec<String> {
    override fun encode(decoded: String): JsonNode = Jsons.textNode(decoded)

    // Use asText() so this works whether the node is a TextNode or any other type.
    override fun decode(encoded: JsonNode): String = encoded.asText()
}
