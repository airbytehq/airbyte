/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.salesforce

import io.airbyte.cdk.load.check.DestinationChecker
import io.airbyte.cdk.load.http.HttpClient
import io.airbyte.cdk.load.http.Request
import io.airbyte.cdk.load.http.RequestMethod
import io.airbyte.cdk.load.http.Response
import java.io.InputStreamReader
import java.util.function.Supplier

class SalesforceChecker(private val httpClient: HttpClient, private val baseUrl: Supplier<String>) :
    DestinationChecker<SalesforceConfiguration> {
    override fun check(config: SalesforceConfiguration) {
        val response: Response =
            httpClient.send(
                Request(
                    method = RequestMethod.GET,
                    url = "${baseUrl.get()}/services/data/v62.0/sobjects/Contact/describe/"
                )
            )

        response.use {
            if (it.statusCode != 200) {
                val responseBody =
                    it.body?.let { body ->
                        InputStreamReader(body, Charsets.UTF_8).use { reader -> reader.readText() }
                    }
                throw IllegalStateException(
                    "Check failed: could not access `Contact` schema. HTTP message is: $responseBody}"
                )
            }
        }
    }
}
