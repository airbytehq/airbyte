/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.destination.s3

import com.fasterxml.jackson.databind.JsonNode
import javax.annotation.Nonnull

open class S3DestinationConfigFactory {
    open fun getS3DestinationConfig(
        config: JsonNode,
        @Nonnull storageProvider: StorageProvider,
        environment: Map<String, String>
    ): S3DestinationConfig {
        return S3DestinationConfig.Companion.getS3DestinationConfig(
            config = config,
            storageProvider = storageProvider,
            environment = environment
        )
    }
}
