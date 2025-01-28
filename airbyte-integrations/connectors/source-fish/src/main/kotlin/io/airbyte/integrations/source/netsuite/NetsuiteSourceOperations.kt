/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.netsuite

import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.command.OpaqueStateValue
import io.airbyte.cdk.discover.FieldType
import io.airbyte.cdk.discover.JdbcAirbyteStreamFactory
import io.airbyte.cdk.discover.JdbcMetadataQuerier
import io.airbyte.cdk.discover.MetaField
import io.airbyte.cdk.discover.SystemType
import io.airbyte.cdk.jdbc.BigIntegerFieldType
import io.airbyte.cdk.jdbc.BytesFieldType
import io.airbyte.cdk.jdbc.DoubleFieldType
import io.airbyte.cdk.jdbc.OffsetDateTimeFieldType
import io.airbyte.cdk.jdbc.PokemonFieldType
import io.airbyte.cdk.jdbc.StringFieldType
import io.airbyte.cdk.read.SelectQuery
import io.airbyte.cdk.read.SelectQueryGenerator
import io.airbyte.cdk.read.SelectQuerySpec
import io.airbyte.cdk.read.Stream
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Primary
import jakarta.inject.Singleton
import java.time.OffsetDateTime

@Singleton
@Primary
class NetsuiteSourceOperations() :
    JdbcMetadataQuerier.FieldTypeMapper, SelectQueryGenerator, JdbcAirbyteStreamFactory {
    private val log = KotlinLogging.logger {}

    override val globalCursor: MetaField? = null

    override val globalMetaFields: Set<MetaField> = emptySet()
    override fun decorateRecordData(
        timestamp: OffsetDateTime,
        globalStateValue: OpaqueStateValue?,
        stream: Stream,
        recordData: ObjectNode
    ) {
        TODO("Not yet implemented")
    }

    override fun toFieldType(c: JdbcMetadataQuerier.ColumnMetadata): FieldType =
        when (val type = c.type) {
            is SystemType -> {
                log.info { "type: ${type.typeName}" }
                when (type.typeName) {
                    "DOUBLE" -> DoubleFieldType
                    "CHAR",
                    "VARCHAR",
                    "VARCHAR2" -> StringFieldType
                    "BIGINT" -> BigIntegerFieldType
                    "TIMESTAMP" -> OffsetDateTimeFieldType
                    "CLOB" -> BytesFieldType
                    else -> PokemonFieldType
                }
            }
            else -> PokemonFieldType
        }

    override fun generate(ast: SelectQuerySpec): SelectQuery =
        SelectQuery("sql", listOf(), listOf())
}
