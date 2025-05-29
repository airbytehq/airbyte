/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.pipline.object_storage.file

import java.util.UUID

/**
 * Generate a unique upload id to keep track of the upload in the case of file name collisions.
 * Factored out for testability.
 */
class UploadIdGenerator {
    fun generate() = UUID.randomUUID().toString()
}
