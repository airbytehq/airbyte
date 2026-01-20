/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.file.object_storage

interface RemoteObject<C> {
    val key: String
    val storageConfig: C
}
