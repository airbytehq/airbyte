/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.netsuite

import com.fasterxml.jackson.databind.JsonNode
import com.nimbusds.jose.JWSAlgorithm
import com.nimbusds.jose.JWSAlgorithm.ES256
import com.nimbusds.jose.JWSAlgorithm.ES384
import com.nimbusds.jose.JWSAlgorithm.ES512
import com.nimbusds.jose.JWSAlgorithm.PS256
import com.nimbusds.jose.JWSAlgorithm.PS384
import com.nimbusds.jose.JWSAlgorithm.PS512
import com.nimbusds.jose.JWSHeader
import com.nimbusds.jose.JWSSigner
import com.nimbusds.jose.crypto.ECDSASigner
import com.nimbusds.jose.crypto.RSASSASigner
import com.nimbusds.jwt.JWTClaimsSet
import com.nimbusds.jwt.SignedJWT
import edu.umd.cs.findbugs.annotations.SuppressFBWarnings
import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.util.Jsons
import io.github.oshai.kotlinlogging.KotlinLogging
import io.ktor.client.*
import io.ktor.client.engine.cio.*
import io.ktor.client.request.forms.*
import io.ktor.client.statement.*
import io.ktor.http.*
import java.io.StringReader
import java.security.PrivateKey
import java.security.interfaces.ECPrivateKey
import java.security.interfaces.RSAPrivateKey
import java.time.Clock
import java.time.Duration
import java.time.Instant
import java.util.*
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.runBlocking
import org.apache.sshd.common.util.security.SecurityUtils

/**
 * How OAuth2 works in SuiteAnalytics connect: The values of client ID, client secret, and private
 * key are used to generate a signed JWT assertion. This assertion is sent to the netsuite token
 * endpoint to obtain an access token. The access token is then used to authenticate jdbc
 * connections to netsuite as follows: The jdbc url is appended with ";OAuth2Token=<access_token>".
 *
 * This is a machine-to-machine authentication (AKA client credentials flow). So no user interaction
 * is required.
 *
 * The access token itself is valid for 60 minutes. Each time the connector is attempting to
 * generate a new connection to netsuite, we check if the previously generated access token is still
 * valid. and in case it needs a refresh, we repeat the process.
 */
private val log = KotlinLogging.logger {}

val SCOPES = listOf("suite_analytics")
val GRANT_TYPE = "client_credentials"
val CLIENT_ASSERTION_TYPE = "urn:ietf:params:oauth:client-assertion-type:jwt-bearer"
const val TOKEN_ENDPOINT_URL_SUFFIX =
    "suitetalk.api.netsuite.com/services/rest/auth/oauth2/v1/token"

fun generateSignedClientAssertion(
    accountId: String,
    oath2Authentication: OAuth2Authentication
): SignedJWT {
    val privateKeyContents = oath2Authentication.oauth2PrivateKey

    val keyPairs =
        SecurityUtils.getKeyPairResourceParser()
            .loadKeyPairs(null, null, null, StringReader(privateKeyContents))

    if (keyPairs.isEmpty()) {
        throw ConfigErrorException("No key pairs found in the provided private key contents.")
    }
    val signer: JWSSigner = generateSignerFromKey(keyPairs.first().private)

    // Netsuite SuiteAnalytics OAuth2 supports PS256, PS384, PS512, ES256, ES384, or ES512 as
    // signing algorithms.
    // https://docs.oracle.com/en/cloud/saas/netsuite/ns-online-help/section_162790605110.html
    val signingAlgorithm: JWSAlgorithm =
        when (signer) {
            is RSASSASigner ->
                signer.supportedJWSAlgorithms().first {
                    it in
                        listOf(
                            PS256,
                            PS384,
                            PS512,
                        )
                }
            is ECDSASigner ->
                signer.supportedJWSAlgorithms().first { it in listOf(ES256, ES384, ES512) }
            else -> throw ConfigErrorException("Unsupported JWT algorithm.")
        }

    val issueInstant: Instant = Instant.now(Clock.systemUTC())

    val claimsSet: JWTClaimsSet =
        JWTClaimsSet.Builder()
            .issuer(oath2Authentication.clientId)
            .claim("scope", SCOPES)
            .audience("https://$accountId.$TOKEN_ENDPOINT_URL_SUFFIX")
            .issueTime(Date.from(issueInstant))
            .expirationTime(Date.from(issueInstant.plus(Duration.ofMinutes(15))))
            .build()

    val signedJwt =
        SignedJWT(
            JWSHeader.Builder(signingAlgorithm).keyID(oath2Authentication.keyId).build(),
            claimsSet
        )
    signedJwt.sign(signer)
    return signedJwt
}

fun generateSignerFromKey(privateKey: PrivateKey): JWSSigner =
    when (privateKey) {
        is ECPrivateKey -> ECDSASigner(privateKey)
        is RSAPrivateKey -> RSASSASigner(privateKey)
        else -> throw ConfigErrorException("Unsupported key type: ${privateKey.algorithm}")
    }

fun generateTokenRequestBody(signedJwt: SignedJWT): Parameters {
    return parameters {
        append("grant_type", GRANT_TYPE)
        append("client_assertion_type", CLIENT_ASSERTION_TYPE)
        append("client_assertion", signedJwt.serialize())
    }
}

/**
 * A dummy empty class is needed to suppress the FindBugs warning which can only applies to classes
 * scope. the warning itself is due to use of Kotlin coroutines and is not a real issue.
 */
@SuppressFBWarnings(value = ["NP_NONNULL_PARAM_VIOLATION"], justification = "Kotlin coroutines")
class DummyFBWarningSuppressor {
    companion object {
        suspend fun getAccessToken(accountId: String, formParameters: Parameters): String {
            val response: HttpResponse =
                HttpClient(CIO).use { client ->
                    val url = "https://$accountId.$TOKEN_ENDPOINT_URL_SUFFIX"
                    log.info { "Getting access token from $url" }
                    client.submitForm(url, formParameters)
                }
            log.info { "Access token call returned ${response.status}" }
            if (response.status != HttpStatusCode.OK) {
                val responseBody = response.bodyAsText(Charsets.UTF_8)
                log.debug {
                    "Access token call returned ${response.status}\n" +
                        "Response body: $responseBody"
                }
                throw ConfigErrorException(
                    "Failed to get access token. call returned ${response.status}.\nCheck configuration and consult with Netsuite's Login Audit Trail"
                )
            }
            val model: JsonNode = Jsons.readTree(response.bodyAsText(Charsets.UTF_8))
            return model.get("access_token").asText()
        }
    }
}

fun oauth2Authenticate(accountId: String, oauth2Authentication: OAuth2Authentication): String {
    val accountIdForUrl = accountId.replace("_", "-")
    val assertion = generateSignedClientAssertion(accountIdForUrl, oauth2Authentication)
    val params = generateTokenRequestBody(assertion)
    var accessToken: String
    runBlocking(Dispatchers.IO) {
        accessToken = DummyFBWarningSuppressor.getAccessToken(accountIdForUrl, params)
    }
    return accessToken
}

fun oauth2GetAccessTokenExpiration(tokenString: String): Date {
    val jwt = SignedJWT.parse(tokenString)
    return jwt.jwtClaimsSet.expirationTime
}
