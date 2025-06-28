/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.teradata.typing_deduping

import com.fasterxml.jackson.databind.node.ObjectNode
import org.junit.jupiter.api.AfterAll
import org.junit.jupiter.api.BeforeAll
import org.junit.jupiter.api.parallel.Execution
import org.junit.jupiter.api.parallel.ExecutionMode

/**
 * Test class for verifying typing and deduplication behavior in the Teradata destination connector.
 *
 * This class extends {@link AbstractTeradataTypingDedupingTest} and provides a concrete
 * implementation configured to test with typing and deduplication enabled.
 *
 * Tests are executed in the same thread to avoid concurrency issues related to Teradata database
 * operations.
 */
@Execution(ExecutionMode.SAME_THREAD)
open class TeradataTypingDedupingTest : AbstractTeradataTypingDedupingTest() {
    /** Specifies the name of the raw schema used for storing raw synced data. */
    private val raw_schema_name = "airbyte_internal"
    /**
     * Instance of ClearScapeManager responsible for managing Teradata test environment lifecycle.
     */
    protected open var clearscapeManager: ClearScapeManager =
        ClearScapeManager("secrets/typing_config.json")

    /** Sets up the Teradata ClearScape environment once before any test runs. */
    @BeforeAll
    fun setupTeradata() {
        clearscapeManager.setup()
    }

    /** Tears down the Teradata ClearScape environment after all tests complete. */
    @AfterAll
    fun teardownTeradata() {
        clearscapeManager.stop()
    }

    /**
     * Returns the base configuration used in this test class.
     *
     * It pulls from the {@link ClearScapeManager} and applies specific overrides:
     * - Sets the raw data schema to "airbyte_internal"
     * - Enables typing and deduplication by setting `disable_type_dedupe` to false
     *
     * @return an updated {@link ObjectNode} with test-specific overrides
     */
    override fun getBaseConfig(): ObjectNode {

        return clearscapeManager.configJSON
            .put("raw_data_schema", raw_schema_name)
            .put("disable_type_dedupe", false)
    }
    /**
     * Indicates whether final table comparison should be skipped.
     *
     * @return false, meaning that final table comparison will be performed after the sync
     */
    override fun disableFinalTableComparison(): Boolean {
        return false
    }
    /**
     * Provides the raw schema name used during the test.
     *
     * @return the string "airbyte_internal" representing the raw schema
     */
    override val rawSchema: String
        get() = raw_schema_name
}
