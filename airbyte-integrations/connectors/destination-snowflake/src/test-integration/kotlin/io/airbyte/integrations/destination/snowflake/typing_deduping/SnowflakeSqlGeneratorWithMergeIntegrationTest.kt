/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.typing_deduping

import io.airbyte.integrations.base.destination.typing_deduping.SqlGenerator

class SnowflakeSqlGeneratorWithMergeIntegrationTest :
    AbstractSnowflakeSqlGeneratorIntegrationTest() {
    override val sqlGenerator: SqlGenerator
        get() = SnowflakeSqlGenerator(0, true)
}
