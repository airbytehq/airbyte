/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.teradata.typing_deduping

import com.fasterxml.jackson.databind.node.ObjectNode
import org.junit.jupiter.api.BeforeAll
import org.junit.jupiter.api.Timeout
import org.junit.jupiter.api.parallel.Execution
import org.junit.jupiter.api.parallel.ExecutionMode

@Execution(ExecutionMode.SAME_THREAD)
class TeradataRawOverrideTypingDedupingTest : TeradataTypingDedupingTest() {
    override fun getBaseConfig(): ObjectNode {
        return super.getBaseConfig().put("raw_data_schema", "overridden_raw_dataset")
    }

    override val rawSchema: String
        get() = "overridden_raw_dataset"

    companion object {
        @JvmStatic
        @BeforeAll
        @Throws(Exception::class)
        @Timeout(1200)
        fun initEnvironment(): Unit {
            base.init("secrets/raw_override_typing_config.json")
        }
    }
}
