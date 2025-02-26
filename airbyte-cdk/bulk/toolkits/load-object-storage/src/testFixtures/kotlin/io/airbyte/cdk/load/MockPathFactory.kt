/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.file.object_storage.PathFactory
import io.airbyte.cdk.load.file.object_storage.PathMatcher
import io.micronaut.context.annotation.Requires
import jakarta.inject.Singleton

@Singleton
@Requires(env = ["MockPathFactory"])
open class MockPathFactory : PathFactory {
    override val finalPrefix: String
        get() = "prefix"

    private fun fromStream(stream: DestinationStream): String {
        return "${stream.descriptor.namespace}/${stream.descriptor.name}"
    }

    override fun getFinalDirectory(
        stream: DestinationStream,
        substituteStreamAndNamespaceOnly: Boolean
    ): String {
        return "$finalPrefix/${fromStream(stream)}"
    }

    override fun getPathToFile(
        stream: DestinationStream,
        partNumber: Long?,
        extension: String?
    ): String {
        val prefix = getFinalDirectory(stream)
        return "${prefix}file"
    }

    override fun getLongestStreamConstantPrefix(
        stream: DestinationStream,
    ): String {
        return getFinalDirectory(stream)
    }

    override fun getPathMatcher(
        stream: DestinationStream,
        suffixPattern: String? // ignored
    ): PathMatcher {
        return PathMatcher(
            regex =
                Regex(
                    "$finalPrefix/(${stream.descriptor.namespace})/(${stream.descriptor.name})/(.*)-(.*)$"
                ),
            variableToIndex = mapOf("part_number" to 4)
        )
    }
}
