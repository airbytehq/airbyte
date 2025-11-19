/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres.operations.types

import com.fasterxml.jackson.core.type.TypeReference
import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.TextNode
import io.airbyte.cdk.data.JsonCodec
import io.airbyte.cdk.data.LeafAirbyteSchemaType
import io.airbyte.cdk.jdbc.JdbcAccessor
import io.airbyte.cdk.jdbc.SymmetricJdbcFieldType
import io.airbyte.cdk.util.Jsons
import java.sql.PreparedStatement
import java.sql.ResultSet
import kotlin.reflect.KClass
import org.postgresql.geometric.PGbox
import org.postgresql.geometric.PGcircle
import org.postgresql.geometric.PGline
import org.postgresql.geometric.PGlseg
import org.postgresql.geometric.PGpath
import org.postgresql.geometric.PGpoint
import org.postgresql.geometric.PGpolygon
import org.postgresql.util.PGobject

open class ObjectFieldType<T : PGobject>(kClass: KClass<T>) :
    SymmetricJdbcFieldType<T>(
        LeafAirbyteSchemaType.STRING,
        ObjectAccessor(kClass),
        ObjectCodec(),
    )

class ObjectAccessor<T : PGobject>(val kClass: KClass<T>) : JdbcAccessor<T> {
    override fun get(rs: ResultSet, colIdx: Int): T? {
        return rs.getObject(colIdx, kClass.java)
    }

    override fun set(stmt: PreparedStatement, paramIdx: Int, value: T) {
        stmt.setString(paramIdx, value.value)
    }
}

class ObjectCodec<T : PGobject>() : JsonCodec<T> {
    override fun encode(decoded: T): JsonNode {
        return TextNode(decoded.value)
    }

    override fun decode(encoded: JsonNode): T {
        return Jsons.readValue(encoded.asText(), object : TypeReference<T>() {})
    }
}

// These need to be defined at compile time to avoid issues with type erasure
object CircleFieldType : ObjectFieldType<PGcircle>(PGcircle::class)

object BoxFieldType : ObjectFieldType<PGbox>(PGbox::class)

object LineFieldType : ObjectFieldType<PGline>(PGline::class)

object LsegFieldType : ObjectFieldType<PGlseg>(PGlseg::class)

object PathFieldType : ObjectFieldType<PGpath>(PGpath::class)

object PointFieldType : ObjectFieldType<PGpoint>(PGpoint::class)

object PolygonFieldType : ObjectFieldType<PGpolygon>(PGpolygon::class)
