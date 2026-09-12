/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.bigqueryv2

import io.airbyte.cdk.command.SyncsTestFixture
import org.junit.jupiter.api.BeforeAll
import org.junit.jupiter.api.Test

/** Runs the CHECK operation against the BigQuery emulator. */
class BigQuerySourceCheckTest {

    @Test
    fun testCheckSucceedsWithDataset() {
        SyncsTestFixture.testCheck(
            BigQueryEmulatorTestFixture.config(datasetId = BigQueryEmulatorTestFixture.DATASET)
        )
    }

    @Test
    fun testCheckSucceedsWithoutDataset() {
        SyncsTestFixture.testCheck(BigQueryEmulatorTestFixture.config())
    }

    @Test
    fun testCheckFailsWithUnknownDataset() {
        SyncsTestFixture.testCheck(
            BigQueryEmulatorTestFixture.config(datasetId = "does_not_exist"),
            expectedFailure = "(?i)not found",
        )
    }

    @Test
    fun testCheckFailsWithUnknownProject() {
        SyncsTestFixture.testCheck(
            BigQueryEmulatorTestFixture.config(projectId = "does-not-exist"),
            expectedFailure = "(?i)not found",
        )
    }

    @Test
    fun testCheckFailsWithDatasetWithoutTables() {
        SyncsTestFixture.testCheck(
            BigQueryEmulatorTestFixture.config(
                datasetId = BigQueryEmulatorTestFixture.EMPTY_DATASET
            ),
            expectedFailure = "Discovered zero tables",
        )
    }

    companion object {
        @JvmStatic
        @BeforeAll
        fun startEmulator() {
            BigQueryEmulatorTestFixture.start()
        }
    }
}
