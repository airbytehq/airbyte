/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.command.gcs

class GcsClientSpecification {}

class GcsClientConfiguration {}

interface GcsClientConfigurationProvider {
    val gcsClientConfiguration: GcsClientConfiguration
}
