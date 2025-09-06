/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.spec

import io.airbyte.cdk.load.command.DestinationConfiguration
import io.airbyte.cdk.load.command.dlq.ObjectStorageConfig
import io.airbyte.cdk.load.command.dlq.ObjectStorageConfigProvider

/**
 * With this class, we are doing a distinction between CDK configuration and connector
 * configuration. A DestinationConfiguration is required to satisfy come of the CDK configuration
 * like the estimatedRecordMemoryOverheadRatio for ReservingDeserializingInputFlow or the
 * DlqPipelineFactoryFactory that requires a DestinationConfiguration that is also a
 * ObjectStorageConfigProvider.
 *
 * In terms of the Declarative framework, we expect the Connector configuration (credentials, API
 * domain, if it is a sandbox environment or not, etc...) to be scopes to
 * DeclarativeDestinationFactory and string interpolation.
 */
class DeclarativeCdkConfiguration(override val objectStorageConfig: ObjectStorageConfig) :
    DestinationConfiguration(), ObjectStorageConfigProvider
