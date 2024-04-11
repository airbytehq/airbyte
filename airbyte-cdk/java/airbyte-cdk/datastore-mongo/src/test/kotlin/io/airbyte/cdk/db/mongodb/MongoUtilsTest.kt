/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.db.mongodb

import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.db.mongodb.MongoUtils.transformToStringIfMarked
import io.airbyte.commons.json.Jsons
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

internal class MongoUtilsTest {
    @Test
    fun testTransformToStringIfMarked() {
        val columnNames =
            listOf("_id", "createdAt", "connectedWallets", "connectedAccounts_aibyte_transform")
        val fieldName = "connectedAccounts"
        val node =
            Jsons.deserialize(
                "{\"_id\":\"12345678as\",\"createdAt\":\"2022-11-11 12:13:14\",\"connectedWallets\":\"wallet1\"," +
                    "\"connectedAccounts\":" +
                    "{\"google\":{\"provider\":\"google\",\"refreshToken\":\"test-rfrsh-google-token-1\",\"accessToken\":\"test-access-google-token-1\",\"expiresAt\":\"2020-09-01T21:07:00Z\",\"createdAt\":\"2020-09-01T20:07:01Z\"}," +
                    "\"figma\":{\"provider\":\"figma\",\"refreshToken\":\"test-rfrsh-figma-token-1\",\"accessToken\":\"test-access-figma-token-1\",\"expiresAt\":\"2020-12-13T22:08:03Z\",\"createdAt\":\"2020-09-14T22:08:03Z\",\"figmaInfo\":{\"teamID\":\"501087711831561793\"}}," +
                    "\"slack\":{\"provider\":\"slack\",\"accessToken\":\"test-access-slack-token-1\",\"createdAt\":\"2020-09-01T20:15:07Z\",\"slackInfo\":{\"userID\":\"UM5AD2YCE\",\"teamID\":\"T2VGY5GH5\"}}}}"
            )
        Assertions.assertTrue(node[fieldName].isObject)

        transformToStringIfMarked((node as ObjectNode), columnNames, fieldName)

        Assertions.assertNull(node[fieldName])
        Assertions.assertNotNull(node[fieldName + MongoUtils.AIRBYTE_SUFFIX])
        Assertions.assertTrue(node[fieldName + MongoUtils.AIRBYTE_SUFFIX].isTextual)
    }
}
