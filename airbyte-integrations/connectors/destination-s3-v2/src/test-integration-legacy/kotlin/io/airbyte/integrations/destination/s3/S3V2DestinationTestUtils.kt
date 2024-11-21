/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.commons.io.IOs.readFile
import io.airbyte.commons.json.Jsons.deserialize
import java.nio.file.Path

object S3V2DestinationTestUtils {
    private const val ASSUME_ROLE_CONFIG_SECRET_PATH = "secrets/s3_dest_assume_role_config.json"
    private const val ASSUME_ROLE_INTERNAL_CREDENTIALS_SECRET_PATH =
        "secrets/s3_dest_iam_role_credentials_for_assume_role_auth.json"

    val assumeRoleConfig: JsonNode
        get() = deserialize(readFile(Path.of(ASSUME_ROLE_CONFIG_SECRET_PATH)))

    private fun getCredentials(secretPath: String): Map<String, String> {
        val retVal = HashMap<String, String>()
        for ((key, value) in deserialize(readFile(Path.of(secretPath))).properties()) {
            retVal[key] = value.textValue()
        }
        return retVal
    }

    val assumeRoleInternalCredentials: Map<String, String>
        get() = getCredentials(ASSUME_ROLE_INTERNAL_CREDENTIALS_SECRET_PATH)
}
