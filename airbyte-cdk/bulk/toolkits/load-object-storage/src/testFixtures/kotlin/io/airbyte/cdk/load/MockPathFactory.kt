/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.file.object_storage.PathFactory
import io.airbyte.cdk.load.file.object_storage.PathMatcher
import io.micronaut.context.annotation.Requires
import jakarta.inject.Singleton
import java.nio.file.Path

@Singleton
@Requires(env = ["MockPathFactory"])
open class MockPathFactory : PathFactory {
    open var doSupportStaging = false

    override val supportsStaging: Boolean
        get() = doSupportStaging
    override val prefix: String
        get() = "prefix"

    private fun fromStream(stream: DestinationStream): String {
        return "/${stream.descriptor.namespace}/${stream.descriptor.name}"
    }

    override fun getStagingDirectory(stream: DestinationStream): Path {
        return Path.of("$prefix/staging/${fromStream(stream)}")
    }

    override fun getFinalDirectory(stream: DestinationStream): Path {
        return Path.of("$prefix/${fromStream(stream)}")
    }

    override fun getPathToFile(
        stream: DestinationStream,
        partNumber: Long?,
        isStaging: Boolean,
        extension: String?
    ): Path {
        val prefix = if (isStaging) getStagingDirectory(stream) else getFinalDirectory(stream)
        return prefix.resolve("file")
    }

    override fun getPathMatcher(stream: DestinationStream): PathMatcher {
        return PathMatcher(
            regex = Regex("$prefix/(.*)-(.*)$"),
            variableToIndex = mapOf("part_number" to 2)
        )
    }
}
