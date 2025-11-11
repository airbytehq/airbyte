/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.http

import io.mockk.mockk
import io.mockk.verify
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test

class HttpRequesterTest {

    lateinit var client: HttpClient

    companion object {
        val METHOD = RequestMethod.GET
    }

    @BeforeEach
    fun setUp() {
        client = mockk(relaxed = true)
    }

    @Test
    internal fun `test given url when send then perform request`() {
        val requester = HttpRequester(client, METHOD, """https://test.com/x""")
        requester.send(mapOf("variable" to "x"))
        verify { client.send(Request(METHOD, "https://test.com/x")) }
    }

    @Test
    internal fun `test given url contains interpolation when send then interpolate url`() {
        val requester = HttpRequester(client, METHOD, """https://test.com/{{ variable }}""")
        requester.send(mapOf("variable" to "x"))
        verify { client.send(Request(METHOD, "https://test.com/x")) }
    }
}
