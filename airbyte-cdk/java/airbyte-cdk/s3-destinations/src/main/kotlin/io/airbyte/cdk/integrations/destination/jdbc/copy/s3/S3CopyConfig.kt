/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.destination.jdbc.copy.s3

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.integrations.destination.s3.S3DestinationConfig

/**
 * S3 copy destinations need an S3DestinationConfig to configure the basic upload behavior. We also
 * want additional flags to configure behavior that only applies to the copy-to-S3 +
 * load-into-warehouse portion. Currently this is just purgeStagingData, but this may expand.
 */
class S3CopyConfig(val purgeStagingData: Boolean, val s3Config: S3DestinationConfig) {

    companion object {
        @JvmStatic
        fun shouldPurgeStagingData(config: JsonNode): Boolean {
            return if (config["purge_staging_data"] == null) {
                true
            } else {
                config["purge_staging_data"].asBoolean()
            }
        }

        fun getS3CopyConfig(config: JsonNode): S3CopyConfig {
            return S3CopyConfig(
                shouldPurgeStagingData(config),
                S3DestinationConfig.Companion.getS3DestinationConfig(config)
            )
        }
    }
}
