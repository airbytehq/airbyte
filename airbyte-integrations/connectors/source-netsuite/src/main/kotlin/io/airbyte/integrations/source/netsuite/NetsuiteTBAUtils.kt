/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.netsuite

import io.github.oshai.kotlinlogging.KotlinLogging
import java.util.Base64
import javax.crypto.Mac
import javax.crypto.spec.SecretKeySpec
import org.apache.commons.lang3.RandomStringUtils

private val log = KotlinLogging.logger {}

/**
 * How TBA works in SuiteAnalytics connect over jdbc: the values of client Id (aka consumer key),
 * client secret, token id and token secret are used to calculate an HMAC sha256 hash on a base
 * string that consists of the following: netsuite account id & client id & token id & nonce &
 * timestamp
 *
 * nonce is randomly generated alphanumeric string of 20 characters. timestamp is current unix time.
 *
 * The value of this string is then hased with a string that consists of: client secret $ token
 * secret
 *
 * In Jdbc connection the username is always "TBA" for token-based authentication, And the password
 * the hashed signature value is used in the following string: base string & signature &
 * "HMAC-SHA256"
 *
 * The signature is valid for 5 minutes. Connecting to netsuite with a token password that was
 * previously used is not allowed A connection is valid for up to 60 minutes
 */
const val USERNAME = "user"
const val PASSWORD = "password"
const val TBA_USER = "TBA"
const val CLIENT_ID = "client_id"
const val CLIENT_SECRET = "client_secret"
const val TOKEN_ID = "token_id"
const val TOKEN_SECRET = "token_secret"

private fun computeShaHash(baseString: String, key: String, algorithm: String): String {
    val bytes: ByteArray = key.toByteArray()
    val signingKey: SecretKeySpec = SecretKeySpec(bytes, algorithm)
    val messageAuthenticationCode: Mac = Mac.getInstance(algorithm)
    messageAuthenticationCode.init(signingKey)
    val hash: ByteArray? = messageAuthenticationCode.doFinal(baseString.toByteArray())
    return String(Base64.getEncoder().encode(hash))
}

private fun computeSignature(
    account: String,
    clientId: String,
    clientSecret: String,
    tokenId: String,
    tokenSecret: String,
    nonce: String,
    timeStamp: Long?
): String {
    val baseString = "$account&$clientId&$tokenId&$nonce&$timeStamp"
    val key = "$clientSecret&$tokenSecret"
    val signature: String = computeShaHash(baseString, key, "HmacSHA256")
    return "$baseString&$signature&HMAC-SHA256"
}

private fun generateNetsuiteOAuth1TokenPassword(
    account: String,
    clientId: String,
    clientSecret: String,
    tokenId: String,
    tokenSecret: String,
): String {

    // Nonce and timeStamp must be unique for each request.
    val nonce: String = RandomStringUtils.secure().nextAlphanumeric(20)
    val timeStamp = System.currentTimeMillis() / 1000L

    val signature: String =
        computeSignature(
            account,
            clientId,
            clientSecret,
            tokenId,
            tokenSecret,
            nonce,
            timeStamp,
        )
    log.debug { "Generated token password: $signature" }
    return signature
}

class OAuth1TokenDispensingJdbcProperties(val base: Map<String, String>, val accountId: String) :
    Map<String, String> by base {
    override val entries: Set<Map.Entry<String, String>>
        get() {
            val tbaJdbcProperties = mutableMapOf<String, String>()
            // calculate the token password for TBA user
            val tbaUser = get(USERNAME)!!
            val tbaPassword = get(PASSWORD)!!

            // Create a clone of all entries with TBA user and password, omitting secret token
            // fields
            keys
                .filterNot {
                    it in
                        listOf(USERNAME, PASSWORD, CLIENT_ID, CLIENT_SECRET, TOKEN_ID, TOKEN_SECRET)
                }
                .forEach { tbaJdbcProperties[it] = get(it)!! }
            tbaJdbcProperties[USERNAME] = tbaUser
            tbaJdbcProperties[PASSWORD] = tbaPassword

            return tbaJdbcProperties.entries
        }

    override fun get(key: String): String? {
        return when (key) {
            // The username is always "TBA" for token-based authentication
            USERNAME -> TBA_USER
            // Netsuite TBA allows single use of a token password. regenerate a fresh one
            PASSWORD ->
                generateNetsuiteOAuth1TokenPassword(
                    accountId,
                    base[CLIENT_ID]!!,
                    base[CLIENT_SECRET]!!,
                    base[TOKEN_ID]!!,
                    base[TOKEN_SECRET]!!
                )
            else -> base[key]
        }
    }

    override fun containsKey(key: String): Boolean {
        return when (key) {
            USERNAME,
            PASSWORD, -> true
            else -> base.contains(key)
        }
    }
}
