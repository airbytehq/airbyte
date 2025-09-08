/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.checker

import io.airbyte.cdk.load.check.DestinationCheckerV2
import io.airbyte.cdk.load.check.dlq.DlqChecker
import io.airbyte.cdk.load.command.dlq.ObjectStorageConfig
import io.mockk.Runs
import io.mockk.every
import io.mockk.impl.annotations.MockK
import io.mockk.junit5.MockKExtension
import io.mockk.just
import io.mockk.verify
import kotlin.test.assertFailsWith
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.extension.ExtendWith

@ExtendWith(MockKExtension::class)
class CompositeDlqCheckerTest {

    @MockK private lateinit var decorated: DestinationCheckerV2

    @MockK private lateinit var dlqChecker: DlqChecker

    @MockK private lateinit var objectStorageConfig: ObjectStorageConfig

    private lateinit var compositeDlqChecker: CompositeDlqChecker

    @BeforeEach
    fun setUp() {
        compositeDlqChecker = CompositeDlqChecker(decorated, dlqChecker, objectStorageConfig)
    }

    @Test
    fun `test given checks successful when check then do not break`() {
        every { decorated.check() } just Runs
        every { dlqChecker.check(objectStorageConfig) } just Runs

        compositeDlqChecker.check()

        verify { decorated.check() }
        verify { dlqChecker.check(objectStorageConfig) }
    }

    @Test
    fun `test given decorated check fails when check then should propagate exception`() {
        every { decorated.check() } throws RuntimeException("Decorated checker failed")
        every { dlqChecker.check(objectStorageConfig) }

        assertFailsWith<RuntimeException> { compositeDlqChecker.check() }
    }

    @Test
    fun `test given dlq checker fails when check then should propagate exception`() {
        every { decorated.check() } just Runs
        every { dlqChecker.check(objectStorageConfig) } throws
            RuntimeException("Decorated checker failed")

        assertFailsWith<RuntimeException> { compositeDlqChecker.check() }
    }

    @Test
    fun `test when cleanup then decorated should cleanup`() {
        every { decorated.cleanup() } just Runs
        compositeDlqChecker.cleanup()
        verify(exactly = 1) { decorated.cleanup() }
    }
}
