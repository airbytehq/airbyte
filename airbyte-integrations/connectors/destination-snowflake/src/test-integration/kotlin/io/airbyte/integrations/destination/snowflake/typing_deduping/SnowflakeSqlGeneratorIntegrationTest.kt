/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.snowflake.typing_deduping

import java.util.*
import org.junit.jupiter.api.*

class SnowflakeSqlGeneratorIntegrationTest : AbstractSnowflakeSqlGeneratorIntegrationTest() {

    override val sqlGenerator: SnowflakeSqlGenerator
        get() = SnowflakeSqlGenerator(0)
}
