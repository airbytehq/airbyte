/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.netsuite

import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

const val account_id = "7111959_SB1"
const val client_id = "0bf3fa15012b535a19852db7c46e0137577c4337e169ea80b3eb65d5be137e37"
const val client_secret = "d46f038b7c7a874b546cfdf8e9bbcd17824504e1f979c05f6791b5d01eb17fc9"
const val token_id = "37c192649edec02e13e10334bb8cf1f21ec6a51bff75124a5a26c6ac2490301a"
const val token_secret = "986d5068cf8a3dd5d0f1be382d648d705acb56ae907f9dd11aa869fec862a9a6"
const val nonce = "LQerHBRF71Glm84H9fxL"
const val timestamp = 1743524381L

const val tokenPassword =
    "7111959_SB1&0bf3fa15012b535a19852db7c46e0137577c4337e169ea80b3eb65d5be137e37&37c192649edec02e13e10334bb8cf1f21ec6a51bff75124a5a26c6ac2490301a&LQerHBRF71Glm84H9fxL&1743524381&7xpNX3vLlf76L/QOkF5g1WfGhO5+9W6mduS6+/+baCQ=&HMAC-SHA256"

class NetsuiteTBAUtilsTest {
    @Test
    fun testSignatureGeneration() {
        Assertions.assertEquals(
            tokenPassword,
            computeSignature(
                account_id,
                client_id,
                client_secret,
                token_id,
                token_secret,
                nonce,
                timestamp
            )
        )
    }

    @Test
    fun testOAuth1TokenDispensingJdbcProperties() {
        val jdbcProperties =
            mapOf(
                CLIENT_ID to client_id,
                CLIENT_SECRET to client_secret,
                TOKEN_ID to token_id,
                TOKEN_SECRET to token_secret,
            )

        val tbaProps = OAuth1TokenDispensingJdbcProperties(jdbcProperties, account_id)

        val m = mutableMapOf<String, String>()
        m.putAll(jdbcProperties)
        Assertions.assertEquals(TBA_USER, tbaProps[USERNAME])
        Assertions.assertNotNull(tbaProps[PASSWORD])
    }
}
