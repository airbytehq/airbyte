/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.azure_blob_storage

import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaInject
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaTitle
import io.airbyte.cdk.command.ConfigurationSpecification
import jakarta.inject.Singleton

@Singleton
@JsonSchemaTitle("Azure Blob Storage Destination Spec")
@JsonSchemaInject()
class AzureBlobStorageSpecification() : ConfigurationSpecification() {}
