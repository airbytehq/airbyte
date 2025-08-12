/* Copyright (c) 2025 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.postgres.operations

import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.command.OpaqueStateValue
import io.airbyte.cdk.discover.FieldOrMetaField
import io.airbyte.cdk.discover.JdbcAirbyteStreamFactory
import io.airbyte.cdk.discover.MetaField
import io.airbyte.cdk.read.Stream
import io.micronaut.context.annotation.Primary
import jakarta.inject.Singleton
import java.time.OffsetDateTime

@Singleton
@Primary
class PostgresSourceStreamFactory : JdbcAirbyteStreamFactory {

    override val globalCursor: FieldOrMetaField = throw NotImplementedError()

    override val globalMetaFields: Set<MetaField> = throw NotImplementedError()

    override fun decorateRecordData(
        timestamp: OffsetDateTime,
        globalStateValue: OpaqueStateValue?,
        stream: Stream,
        recordData: ObjectNode
    ) {
        throw NotImplementedError()
    }
}
