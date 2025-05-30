/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.http

// TODO import dev.failsafe.RetryPolicy
// val failsafeCall = FailsafeCall.with(policy).compose(call)
// val response: Response = failsafeCall.execute()
import io.airbyte.cdk.load.http.authentication.OAuthAuthenticator
import io.airbyte.cdk.load.http.authentication.SalesforceOperationRepository
import okhttp3.OkHttpClient


val clientId: String = "<redacted>"
val clientSecret: String = "<redacted>"
val refreshToken: String = "<redacted>";

val isSandbox: Boolean = true

fun main() {
    val authEndpoint: String = "https://${if (isSandbox) "test" else "login"}.salesforce.com/services/oauth2/token"
    val authenticator: OAuthAuthenticator = OAuthAuthenticator(authEndpoint, clientId, clientSecret, refreshToken)
    val baseUrl: String = authenticator.queryForAccessToken().get("instance_url").asText()

    val httpClient: OkHttpClient = OkHttpClient.Builder().addInterceptor(authenticator).build()
    val operations = SalesforceOperationRepository(httpClient, baseUrl).fetchAll()
    println("DONE")
}
