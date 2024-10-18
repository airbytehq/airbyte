/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.file

import io.micronaut.context.annotation.Secondary
import jakarta.inject.Singleton
import java.nio.file.Files
import java.nio.file.Path

interface TempFileProvider {
    fun createTempFile(directory: Path, prefix: String, suffix: String): LocalFile
}

@Singleton
@Secondary
class DefaultTempFileProvider : TempFileProvider {
    override fun createTempFile(directory: Path, prefix: String, suffix: String): LocalFile {
        Files.createDirectories(directory)
        return DefaultLocalFile(Files.createTempFile(directory, prefix, suffix))
    }
}
