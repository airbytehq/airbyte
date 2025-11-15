/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package bean

import io.airbyte.cdk.load.MockObjectStorageClient
import io.airbyte.cdk.load.file.object_storage.ObjectStorageClient
import io.micronaut.context.annotation.Factory
import jakarta.inject.Singleton

@Factory
class HubSpotTestingOverrideFactory {
    @Singleton fun objectClient(): ObjectStorageClient<*> = MockObjectStorageClient()
}
