/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.write

import io.airbyte.cdk.load.test.util.NameMapper
import io.airbyte.integrations.destination.snowflake.schema.toSnowflakeCompatibleName

class SnowflakeNameMapper : NameMapper {
    override fun mapFieldName(path: List<String>): List<String> =
        path.map { it.toSnowflakeCompatibleName() }
}
