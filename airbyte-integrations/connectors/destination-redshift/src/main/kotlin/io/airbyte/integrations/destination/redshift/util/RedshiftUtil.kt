/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.redshift.util

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.integrations.destination.redshift.constants.RedshiftDestinationConstants
import io.github.oshai.kotlinlogging.KotlinLogging

/** Helper class for Destination Redshift connector. */
private val log = KotlinLogging.logger {}

object RedshiftUtil {
    /**
     * We check whether config located in root of node. (This check is done for Backward
     * compatibility)
     *
     * @param config Configuration parameters
     * @return JSON representation of the configuration
     */
    @JvmStatic
    fun findS3Options(config: JsonNode): JsonNode {
        return if (config.has(RedshiftDestinationConstants.UPLOADING_METHOD))
            config[RedshiftDestinationConstants.UPLOADING_METHOD]
        else config
    }

    @JvmStatic
    fun anyOfS3FieldsAreNullOrEmpty(jsonNode: JsonNode): Boolean {
        return (isNullOrEmpty(jsonNode["s3_bucket_name"]) &&
            isNullOrEmpty(jsonNode["s3_bucket_region"]) &&
            isNullOrEmpty(jsonNode["access_key_id"]) &&
            isNullOrEmpty(jsonNode["secret_access_key"]))
    }

    private fun isNullOrEmpty(jsonNode: JsonNode?): Boolean {
        return null == jsonNode || "" == jsonNode.asText()
    }
}
