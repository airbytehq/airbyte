/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.checker

import io.airbyte.cdk.load.check.DestinationCheckerV2
import io.airbyte.cdk.load.http.HttpRequester
import io.airbyte.cdk.load.http.consumeBodyToString

class HttpRequestChecker(private val requester: HttpRequester) : DestinationCheckerV2 {
    override fun check() {
        val response = requester.send()
        response.use {
            if (it.statusCode != 200) {
                throw IllegalStateException(
                    "Expected status code to be 200 but was ${it.statusCode} with response body ${it.consumeBodyToString()}"
                )
            }
        }
    }
}
