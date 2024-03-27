/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.commons.logging

import org.assertj.core.api.Assertions
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test
import org.slf4j.MDC

internal class MdcScopeTest {
    @BeforeEach
    fun init() {
        MDC.setContextMap(originalMap)
    }

    @Test
    fun testMDCModified() {
        MdcScope(modificationInMDC).use { ignored ->
            val mdcState = MDC.getCopyOfContextMap()
            Assertions.assertThat(mdcState)
                .containsExactlyInAnyOrderEntriesOf(
                    java.util.Map.of(
                        "test",
                        "entry",
                        "new",
                        "will be added",
                        "testOverride",
                        "will override"
                    )
                )
        }
    }

    @Test
    fun testMDCRestore() {
        MdcScope(modificationInMDC).use { ignored -> }
        val mdcState = MDC.getCopyOfContextMap()

        Assertions.assertThat(mdcState).containsAllEntriesOf(originalMap)
        Assertions.assertThat(mdcState).doesNotContainKey("new")
    }

    companion object {
        private val originalMap: Map<String, String> =
            java.util.Map.of("test", "entry", "testOverride", "should be overrided")

        private val modificationInMDC: Map<String, String> =
            java.util.Map.of("new", "will be added", "testOverride", "will override")
    }
}
