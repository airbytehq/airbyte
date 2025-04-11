/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.teradata.typing_deduping

import com.fasterxml.jackson.databind.node.ObjectNode
import org.junit.jupiter.api.BeforeAll
import org.junit.jupiter.api.Disabled
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.Timeout
import org.junit.jupiter.api.parallel.Execution
import org.junit.jupiter.api.parallel.ExecutionMode

@Execution(ExecutionMode.SAME_THREAD)
class TeradataRawOverrideDisableTypingDedupingTest : TeradataTypingDedupingTest() {
    override fun getBaseConfig(): ObjectNode {
        return super.getBaseConfig()
            .put("raw_data_schema", "overridden_raw_dataset")
            .put("disable_type_dedupe", true)
    }

    override val rawSchema: String
        get() = "overridden_raw_dataset"

    override fun disableFinalTableComparison(): Boolean {
        return true
    }

    @Disabled @Test override fun identicalNameSimultaneousSync() {}

    companion object {
        @JvmStatic
        @BeforeAll
        @Throws(Exception::class)
        @Timeout(1200)
        fun initEnvironment(): Unit {
            base.init("secrets/disable_typing_config.json")
        }
    }
}
