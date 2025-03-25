/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.azure_blob_storage

import io.airbyte.cdk.load.write.object_storage.ObjectLoader
import javax.inject.Singleton

// TODO we'll eventually want to override various performance values here, maybe
@Singleton class AzureBlobStorageObjectLoader : ObjectLoader
