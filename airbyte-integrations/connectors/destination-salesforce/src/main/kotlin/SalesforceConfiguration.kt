/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.salesforce

import io.airbyte.cdk.load.command.DestinationConfiguration
import io.airbyte.cdk.load.command.dlq.ObjectStorageConfig
import io.airbyte.cdk.load.command.dlq.ObjectStorageConfigProvider

data class SalesforceConfiguration(
    val clientId: String,
    val clientSecret: String,
    val refreshToken: String,
    val isSandbox: Boolean,
    override val objectStorageConfig: ObjectStorageConfig,
) : DestinationConfiguration(), ObjectStorageConfigProvider
