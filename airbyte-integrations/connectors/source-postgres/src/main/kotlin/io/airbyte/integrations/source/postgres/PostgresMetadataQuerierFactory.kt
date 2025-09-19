/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres

import io.airbyte.cdk.check.JdbcCheckQueries
import io.airbyte.cdk.command.JdbcSourceConfiguration
import io.airbyte.cdk.discover.JdbcMetadataQuerier
import io.airbyte.cdk.discover.JdbcMetadataQuerier.FieldTypeMapper
import io.airbyte.cdk.discover.MetadataQuerier
import io.airbyte.cdk.jdbc.DefaultJdbcConstants
import io.airbyte.cdk.read.SelectQueryGenerator
import io.micronaut.context.annotation.Primary
import jakarta.inject.Singleton

@Singleton
@Primary
class PostgresMetadataQuerierFactory(
    val selectQueryGenerator: SelectQueryGenerator,
    val fieldTypeMapper: FieldTypeMapper,
    val checkQueries: JdbcCheckQueries,
    val constants: DefaultJdbcConstants,
) : MetadataQuerier.Factory<JdbcSourceConfiguration> {
    override fun session(config: JdbcSourceConfiguration): MetadataQuerier {
        val jdbcConnectionFactory = PostgresSourceJdbcConnectionFactory(config)
        return JdbcMetadataQuerier(
            constants,
            config,
            selectQueryGenerator,
            fieldTypeMapper,
            checkQueries,
            jdbcConnectionFactory
        )
    }
}
