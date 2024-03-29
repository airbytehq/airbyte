/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.destination.s3

import com.fasterxml.jackson.databind.JsonNode
import javax.annotation.Nonnull

class S3DestinationConfigFactory {
    fun getS3DestinationConfig(
        config: JsonNode,
        @Nonnull storageProvider: StorageProvider
    ): S3DestinationConfig {
        return S3DestinationConfig.Companion.getS3DestinationConfig(config, storageProvider)
    }
}
