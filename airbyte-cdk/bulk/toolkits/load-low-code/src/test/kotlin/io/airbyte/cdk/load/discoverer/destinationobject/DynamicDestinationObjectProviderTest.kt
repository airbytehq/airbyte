/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.discoverer.destinationobject

import io.airbyte.cdk.load.http.Retriever
import io.airbyte.cdk.util.Jsons
import io.mockk.every
import io.mockk.mockk
import kotlin.test.assertEquals
import kotlin.test.assertFailsWith
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test

class DynamicDestinationObjectProviderTest {

    lateinit var provider: DynamicDestinationObjectProvider
    lateinit var retriever: Retriever

    companion object {
        const val NAME_PATH = "name"
    }

    @BeforeEach
    fun setUp() {
        retriever = mockk()
        provider = DynamicDestinationObjectProvider(retriever, listOf(NAME_PATH))
    }

    @Test
    internal fun `test when get then return all objects`() {
        every { retriever.getAll() } returns
            listOf(
                Jsons.objectNode().put("name", "objectname1"),
                Jsons.objectNode().put("name", "objectname2")
            )
        val objects = provider.get()
        assertEquals(listOf("objectname1", "objectname2"), objects.map { it.name })
    }

    @Test
    internal fun `test given name not found when get then throw illegal argument exception`() {
        every { retriever.getAll() } returns listOf(Jsons.objectNode().put("namenotfound", "-"))
        assertFailsWith<IllegalArgumentException> { provider.get() }
    }
}
