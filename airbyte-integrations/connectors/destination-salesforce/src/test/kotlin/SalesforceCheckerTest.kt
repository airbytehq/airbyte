/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

import io.airbyte.cdk.load.check.dlq.DlqChecker
import io.airbyte.cdk.load.command.dlq.DisabledObjectStorageConfig
import io.airbyte.cdk.load.http.HttpClient
import io.airbyte.cdk.load.http.Request
import io.airbyte.cdk.load.http.RequestMethod
import io.airbyte.cdk.load.http.Response
import io.airbyte.integrations.destination.salesforce.SalesforceChecker
import io.airbyte.integrations.destination.salesforce.SalesforceConfiguration
import io.mockk.every
import io.mockk.mockk
import io.mockk.verify
import java.lang.IllegalStateException
import kotlin.test.assertFailsWith
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test

const val BASE_URL: String = "https://base-url.com"

class SalesforceCheckerTest {

    private lateinit var response: Response
    private lateinit var config: SalesforceConfiguration
    private lateinit var httpClient: HttpClient
    private lateinit var checker: SalesforceChecker
    private lateinit var dlqChecker: DlqChecker

    @BeforeEach
    fun setUp() {
        response = mockk()
        every { response.close() } returns Unit
        config =
            SalesforceConfiguration(
                clientId = "client-id",
                clientSecret = "client-secret",
                refreshToken = "refresh-token",
                isSandbox = true,
                objectStorageConfig = DisabledObjectStorageConfig()
            )
        httpClient = mockk()
        dlqChecker = mockk(relaxed = true)
        checker =
            SalesforceChecker(
                httpClient = httpClient,
                baseUrl = { BASE_URL },
                dlqChecker = dlqChecker,
            )
    }

    @Test
    internal fun `test given response status 200 when decode then do nothing`() {
        every { response.statusCode } returns 200
        every {
            httpClient.send(
                Request(
                    method = RequestMethod.GET,
                    url = "$BASE_URL/services/data/v62.0/sobjects/Contact/describe/"
                )
            )
        } returns response

        checker.check(config)

        verify { dlqChecker.check(config.objectStorageConfig) }
    }

    @Test
    internal fun `test given response status is not 200 when decode then throw error`() {
        every { response.statusCode } returns 401
        every { response.body } returns "any body".byteInputStream()
        every { httpClient.send(any()) } returns response

        assertFailsWith<IllegalStateException>(block = { checker.check(config) })
    }
}
