/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.file

import io.airbyte.cdk.load.command.DestinationConfiguration
import io.micronaut.context.annotation.Secondary
import jakarta.inject.Singleton
import java.nio.file.Files
import java.nio.file.Path

interface SpillFileProvider {
    fun createTempFile(): Path
}

@Singleton
@Secondary
class DefaultSpillFileProvider(val config: DestinationConfiguration) : SpillFileProvider {
    override fun createTempFile(): Path {
        return Files.createTempFile("staged-raw-records", ".jsonl")
    }
}
