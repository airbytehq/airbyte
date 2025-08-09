/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.pipline.object_storage.file

import java.io.File

/**
 * Exists to make it easier to test file access (read, delete, etc.) by injecting a mock factory.
 */
class FileHandleFactory {
    fun make(pathname: String) = FileHandle(pathname)
}

/**
 * File in Kotlin has built-n extensions cannot be directly mocked. This wrapper allows us to mock.
 */
class FileHandle(pathName: String) {
    private val file = File(pathName)

    fun delete() = file.delete()
    fun inputStream() = file.inputStream()
}
