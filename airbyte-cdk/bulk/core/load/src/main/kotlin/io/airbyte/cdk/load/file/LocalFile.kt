/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.file

import io.micronaut.context.annotation.DefaultImplementation
import java.io.Closeable
import java.nio.file.Files
import java.nio.file.Path
import kotlin.streams.asSequence

/**
 * Simple wrappers around java's file interface. This is for testability, and to allow us to do
 * resource management, etc in one place.
 */
interface FileWriter : Closeable {
    fun write(str: String)
    override fun close()
}

interface FileReader : Closeable {
    fun lines(): Sequence<String>
    override fun close()
}

@DefaultImplementation(DefaultLocalFile::class)
interface LocalFile {
    val path: Path
    fun toFileWriter(): FileWriter
    fun toFileReader(): FileReader
    fun delete()
}

class DefaultLocalFile(override val path: Path) : LocalFile {
    override fun toFileWriter(): FileWriter {
        return object : FileWriter {
            private val writer = Files.newBufferedWriter(path)
            override fun write(str: String) {
                writer.write(str)
            }

            override fun close() {
                writer.close()
            }
        }
    }

    override fun toFileReader(): FileReader {
        return object : FileReader {
            private val reader = Files.newBufferedReader(path)
            override fun lines(): Sequence<String> {
                return reader.lines().asSequence()
            }

            override fun close() {
                reader.close()
            }
        }
    }

    override fun delete() {
        Files.delete(path)
    }
}
