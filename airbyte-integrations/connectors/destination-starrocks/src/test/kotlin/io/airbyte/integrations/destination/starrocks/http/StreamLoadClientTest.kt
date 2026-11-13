/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.starrocks.http

import okhttp3.mockwebserver.MockResponse
import okhttp3.mockwebserver.MockWebServer
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertFalse
import org.junit.jupiter.api.Assertions.assertNotNull
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test

class StreamLoadClientTest {

    /**
     * The core regression guard: the FE answers with a 307 to the BE on a different port, and the
     * `Authorization` header must still be present on the redirected (BE) request. OkHttp would
     * otherwise refuse to follow a PUT 307 at all and would strip auth cross-host.
     */
    @Test
    fun `preserves Authorization and body across the FE-to-BE 307 redirect`() {
        val be = MockWebServer().apply { start() }
        be.enqueue(
            MockResponse()
                .setResponseCode(200)
                .setBody(
                    """{"TxnId":1,"Label":"L1","Status":"Success","Message":"OK",
                   "NumberTotalRows":3,"NumberLoadedRows":3,"NumberFilteredRows":0}""",
                ),
        )

        val fe = MockWebServer().apply { start() }
        fe.enqueue(
            MockResponse()
                .setResponseCode(307)
                .setHeader("Location", be.url("/api/db/t/_stream_load").toString()),
        )

        val client =
            StreamLoadClient(
                host = fe.hostName,
                httpPort = fe.port,
                username = "root",
                password = "pw",
                expectContinue = false
            )

        val resp =
            client.streamLoad(
                database = "db",
                table = "t",
                label = "L1",
                headers = mapOf("format" to "csv", "column_separator" to ","),
                body = "1,a\n2,b\n3,c\n".toByteArray(),
            )

        assertEquals("Success", resp.status)
        assertTrue(resp.isSuccess)
        assertEquals(3, resp.loadedRows)

        val feReq = fe.takeRequest()
        assertEquals("PUT", feReq.method)
        assertNotNull(feReq.getHeader("Authorization"))

        val beReq = be.takeRequest()
        assertEquals("PUT", beReq.method)
        assertNotNull(
            beReq.getHeader("Authorization")
        ) // null if OkHttp had auto-followed + stripped
        assertEquals("L1", beReq.getHeader("label"))
        assertEquals("csv", beReq.getHeader("format"))
        assertEquals("1,a\n2,b\n3,c\n", beReq.body.readUtf8())

        fe.shutdown()
        be.shutdown()
    }

    @Test
    fun `parses a logical failure even though HTTP is 200`() {
        val be = MockWebServer().apply { start() }
        be.enqueue(
            MockResponse()
                .setResponseCode(200)
                .setBody(
                    """{"Status":"Fail","Message":"too many filtered rows",
                   "NumberLoadedRows":0,"NumberFilteredRows":5,
                   "ErrorURL":"https://be/api/_load_error_log?file=x"}""",
                ),
        )
        val fe = MockWebServer().apply { start() }
        fe.enqueue(
            MockResponse()
                .setResponseCode(307)
                .setHeader("Location", be.url("/api/db/t/_stream_load").toString()),
        )

        val client =
            StreamLoadClient(
                host = fe.hostName,
                httpPort = fe.port,
                username = "root",
                password = "pw",
                expectContinue = false
            )
        val resp = client.streamLoad("db", "t", "L2", emptyMap(), "x".toByteArray())

        assertEquals("Fail", resp.status)
        assertFalse(resp.isSuccess)
        assertEquals(5, resp.filteredRows)
        assertNotNull(resp.errorUrl)

        fe.shutdown()
        be.shutdown()
    }
}
