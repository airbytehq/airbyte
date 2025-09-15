/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.db

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.orchestration.db.FinalTableNameGenerator
import io.airbyte.cdk.load.orchestration.db.TableName
import io.airbyte.integrations.destination.snowflake.spec.SnowflakeConfiguration
import jakarta.inject.Singleton

@Singleton
class SnowflakeFinalTableNameGenerator(
    private val config: SnowflakeConfiguration,
) : FinalTableNameGenerator {
    override fun getTableName(streamDescriptor: DestinationStream.Descriptor): TableName =
        TableName(
            namespace = streamDescriptor.namespace ?: config.schema,
            name = streamDescriptor.name
        )
}
