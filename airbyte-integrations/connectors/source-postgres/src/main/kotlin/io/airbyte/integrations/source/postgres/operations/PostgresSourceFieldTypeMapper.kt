/* Copyright (c) 2025 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.postgres.operations

import io.airbyte.cdk.discover.FieldType
import io.airbyte.cdk.discover.JdbcMetadataQuerier
import io.micronaut.context.annotation.Primary
import jakarta.inject.Singleton

@Singleton
@Primary
class PostgresSourceFieldTypeMapper : JdbcMetadataQuerier.FieldTypeMapper {

    override fun toFieldType(c: JdbcMetadataQuerier.ColumnMetadata): FieldType {
        // TODO: implement field type mapping
        throw NotImplementedError()
    }
}
