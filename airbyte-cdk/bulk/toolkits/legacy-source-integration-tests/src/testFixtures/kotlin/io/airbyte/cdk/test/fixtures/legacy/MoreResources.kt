/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.test.fixtures.legacy

import com.google.common.base.Preconditions
import com.google.common.io.Resources
import java.io.File
import java.io.IOException
import java.net.URISyntaxException
import java.nio.charset.StandardCharsets
import java.nio.file.FileSystems
import java.nio.file.Files
import java.nio.file.Path
import java.util.stream.Stream

object MoreResources {
    private const val UNSTABLE_API_USAGE = "UnstableApiUsage"

    @JvmStatic
    @Throws(IOException::class)
    fun readResource(name: String): String {
        val resource = Resources.getResource(name)
        return Resources.toString(resource, StandardCharsets.UTF_8)
    }

    @Throws(IOException::class)
    fun readResource(klass: Class<*>, name: String): String {
        val rootedName = if (!name.startsWith("/")) String.format("/%s", name) else name
        val url = Resources.getResource(klass, rootedName)
        return Resources.toString(url, StandardCharsets.UTF_8)
    }

    @Throws(URISyntaxException::class)
    fun readResourceAsFile(name: String): File {
        return File(Resources.getResource(name).toURI())
    }

    @Throws(IOException::class)
    fun readBytes(name: String): ByteArray {
        val resource = Resources.getResource(name)
        return Resources.toByteArray(resource)
    }

    /**
     * This class is a bit of a hack. Might have unexpected behavior.
     *
     * @param klass class whose resources will be access
     * @param name path to directory in resources list
     * @return stream of paths to each resource file. THIS STREAM MUST BE CLOSED.
     * @throws IOException you never know when you IO.
     */
    @Throws(IOException::class)
    fun listResources(klass: Class<*>, name: String): Stream<Path> {
        Preconditions.checkNotNull(klass)
        Preconditions.checkNotNull(name)
        Preconditions.checkArgument(!name.isBlank())

        try {
            val rootedResourceDir = if (!name.startsWith("/")) String.format("/%s", name) else name
            val url = klass.getResource(rootedResourceDir)
            // noinspection ConstantConditions
            Preconditions.checkNotNull(url, "Could not find resource.")

            val searchPath: Path
            if (url.toString().startsWith("jar")) {
                val fileSystem = FileSystems.newFileSystem(url.toURI(), emptyMap<String, Any>())
                searchPath = fileSystem.getPath(rootedResourceDir)
                return Files.walk(searchPath, 1).onClose {
                    Exceptions.toRuntime { fileSystem.close() }
                }
            } else {
                searchPath = Path.of(url.toURI())
                return Files.walk(searchPath, 1)
            }
        } catch (e: URISyntaxException) {
            throw RuntimeException(e)
        }
    }
}
