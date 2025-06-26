/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.pipline.object_storage.file

import io.airbyte.cdk.load.util.UUIDGenerator
import jakarta.inject.Singleton

/**
 * Generate a unique upload id to keep track of the upload in the case of file name collisions.
 * Factored out for testability.
 */
@Singleton
class UploadIdGenerator(
    private val uuidGenerator: UUIDGenerator,
) {
    fun generate() = uuidGenerator.v7().toString()
}
