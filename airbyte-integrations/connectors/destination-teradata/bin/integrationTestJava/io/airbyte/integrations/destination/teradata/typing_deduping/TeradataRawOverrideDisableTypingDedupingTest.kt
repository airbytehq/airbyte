/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.teradata.typing_deduping

import com.fasterxml.jackson.databind.node.ObjectNode
import org.junit.jupiter.api.parallel.Execution
import org.junit.jupiter.api.parallel.ExecutionMode

/**
 * Test class for validating Teradata destination behavior when typing and deduplication are
 * disabled.
 *
 * This class extends {@link TeradataRawOverrideTypingDedupingTest} and overrides the default
 * configuration to explicitly disable typing and deduplication logic.
 *
 * The final table comparison is also disabled since no deduping or schema enforcement is applied.
 */
@Execution(ExecutionMode.SAME_THREAD)
class TeradataRawOverrideDisableTypingDedupingTest : TeradataRawOverrideTypingDedupingTest() {
    /**
     * Instance of ClearScapeManager responsible for managing Teradata test environment lifecycle.
     */
    override var clearscapeManager: ClearScapeManager =
        ClearScapeManager("secrets/disable_typing_config.json")
    /**
     * Overrides the base configuration to include the `disable_type_dedupe = true` flag, which
     * disables Airbyte's type inference and deduplication logic for the sync.
     *
     * @return the modified configuration with type/dedupe disabled
     */
    override fun getBaseConfig(): ObjectNode {
        return super.getBaseConfig().put("disable_type_dedupe", true)
    }
    /**
     * Disables comparison of final table contents after sync, since the deduping is turned off.
     *
     * @return true indicating final table comparison should be skipped
     */
    override fun disableFinalTableComparison(): Boolean {
        return true
    }
}
