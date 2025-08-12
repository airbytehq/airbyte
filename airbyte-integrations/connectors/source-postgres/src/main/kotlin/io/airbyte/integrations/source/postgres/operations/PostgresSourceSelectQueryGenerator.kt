/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres.operations

import io.airbyte.cdk.read.SelectQuery
import io.airbyte.cdk.read.SelectQueryGenerator
import io.airbyte.cdk.read.SelectQuerySpec
import io.micronaut.context.annotation.Primary
import jakarta.inject.Singleton

@Singleton
@Primary
class PostgresSourceSelectQueryGenerator : SelectQueryGenerator {

    override fun generate(ast: SelectQuerySpec): SelectQuery =
        // TODO: implement query generation
        throw NotImplementedError()
}
