/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.teradata.typing_deduping

import com.fasterxml.jackson.databind.node.ObjectNode
import org.junit.jupiter.api.parallel.Execution
import org.junit.jupiter.api.parallel.ExecutionMode

/**
 * Test class that customizes the behavior of {@link TeradataTypingDedupingTest} by overriding the
 * default raw schema and typing/deduplication settings.
 *
 * This test targets scenarios where the raw data schema is explicitly set and typing/deduplication
 * is enabled, allowing verification of correct handling of overridden raw schema configurations.
 *
 * Tests are executed sequentially using {@link ExecutionMode#SAME_THREAD} to avoid issues with
 * concurrent database access in Teradata environments.
 */
@Execution(ExecutionMode.SAME_THREAD)
open class TeradataRawOverrideTypingDedupingTest : TeradataTypingDedupingTest() {

    /**
     * Instance of ClearScapeManager responsible for managing Teradata test environment lifecycle.
     */
    override var clearscapeManager: ClearScapeManager =
        ClearScapeManager("secrets/raw_override_typing_config.json")
    /**
     * Provides the base configuration with custom overrides.
     *
     * This configuration:
     * - Sets a custom raw data schema to "overridden_raw_dataset".
     * - Ensures typing and deduplication are enabled by setting `disable_type_dedupe` to false.
     *
     * @return an updated {@link ObjectNode} containing the test configuration
     */
    override fun getBaseConfig(): ObjectNode {
        return super.getBaseConfig()
            .put("raw_data_schema", "overridden_raw_dataset")
            .put("disable_type_dedupe", false)
    }
    /**
     * Indicates whether the final table comparison should be disabled.
     *
     * @return false, enabling final table comparison after sync
     */
    override fun disableFinalTableComparison(): Boolean {
        return false
    }
    /**
     * Provides the name of the raw schema used during the test.
     *
     * @return the string "overridden_raw_dataset" as the raw schema
     */
    override val rawSchema: String
        get() = "overridden_raw_dataset"
}
