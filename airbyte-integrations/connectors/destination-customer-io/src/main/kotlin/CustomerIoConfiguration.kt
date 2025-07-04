/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.customerio

import io.airbyte.cdk.load.command.DestinationConfiguration
import io.airbyte.cdk.load.command.dlq.ObjectStorageConfig
import io.airbyte.cdk.load.command.dlq.ObjectStorageConfigProvider

data class CustomerIoCredentialsConfig(val siteId: String, val apiKey: String)

data class CustomerIoConfiguration(
    val credentials: CustomerIoCredentialsConfig,
    override val objectStorageConfig: ObjectStorageConfig,
) : DestinationConfiguration(), ObjectStorageConfigProvider
