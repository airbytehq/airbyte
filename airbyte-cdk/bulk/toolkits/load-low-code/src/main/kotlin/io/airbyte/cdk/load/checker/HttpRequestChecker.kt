/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.checker

import io.airbyte.cdk.load.check.DestinationChecker
import io.airbyte.cdk.load.command.DestinationConfiguration
import io.airbyte.cdk.load.http.HttpRequester
import io.airbyte.cdk.load.http.consumeBodyToString

class HttpRequestChecker<C : DestinationConfiguration>(private val requester: HttpRequester) :
    DestinationChecker<C> {
    override fun check(config: C) {
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
