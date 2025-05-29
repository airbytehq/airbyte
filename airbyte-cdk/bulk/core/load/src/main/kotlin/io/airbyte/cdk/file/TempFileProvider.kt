/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.file

import io.micronaut.context.annotation.DefaultImplementation
import java.nio.file.Files
import java.nio.file.Path

@DefaultImplementation(DefaultTempFileProvider::class)
interface TempFileProvider {
    fun createTempFile(directory: Path, prefix: String, suffix: String): LocalFile
}

class DefaultTempFileProvider : TempFileProvider {
    override fun createTempFile(directory: Path, prefix: String, suffix: String): LocalFile {
        return DefaultLocalFile(Files.createTempFile(directory, prefix, suffix))
    }
}
