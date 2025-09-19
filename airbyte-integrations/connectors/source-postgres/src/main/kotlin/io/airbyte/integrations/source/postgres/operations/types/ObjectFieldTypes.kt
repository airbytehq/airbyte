/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres.operations.types

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.TextNode
import io.airbyte.cdk.data.JsonEncoder
import io.airbyte.cdk.data.LeafAirbyteSchemaType
import io.airbyte.cdk.jdbc.JdbcFieldType
import io.airbyte.cdk.jdbc.JdbcGetter
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
    JdbcFieldType<T>(
        LeafAirbyteSchemaType.STRING,
        ObjectGetter(kClass),
        ObjectEncoder(),
    )

class ObjectGetter<T : PGobject>(val kClass: KClass<T>) : JdbcGetter<T> {
    override fun get(rs: ResultSet, colIdx: Int): T? {
        return rs.getObject(colIdx, kClass.java)
    }
}

class ObjectEncoder<T : PGobject>() : JsonEncoder<T> {
    override fun encode(decoded: T): JsonNode {
        return TextNode(decoded.value)
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
