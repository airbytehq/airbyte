package io.airbyte.cdk.load.checker

import io.airbyte.cdk.load.check.DestinationChecker
import io.airbyte.cdk.load.command.DestinationConfiguration
import io.airbyte.cdk.load.http.HttpRequester

class HttpRequestChecker<C : DestinationConfiguration>(
    private val requester: HttpRequester
): DestinationChecker<C> {
    override fun check(config: C) {
        val response = requester.send()
        response.use { assert(it.statusCode == 200, {"Expected status code to be 200 but was ${it.statusCode}"}) }
    }
}
