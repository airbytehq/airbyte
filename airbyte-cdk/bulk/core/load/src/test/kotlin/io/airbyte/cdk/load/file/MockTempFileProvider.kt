/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.file

import io.micronaut.context.annotation.Requires
import jakarta.inject.Singleton
import java.nio.file.Path

@Singleton
@Requires(env = ["MockTempFileProvider"])
class MockTempFileProvider : TempFileProvider {
    class MockLocalFile : LocalFile {
        val writtenLines: MutableList<String> = mutableListOf()
        var linesToRead: MutableList<String> = mutableListOf()
        val writersCreated: MutableList<MockFileWriter> = mutableListOf()
        val readersCreated: MutableList<MockFileReader> = mutableListOf()
        var isDeleted: Boolean = false

        class MockFileWriter(val file: MockLocalFile) : FileWriter {
            var isClosed = false

            override fun write(str: String) {
                file.writtenLines.add(str)
            }

            override fun close() {
                isClosed = true
            }
        }

        class MockFileReader(val file: MockLocalFile) : FileReader {
            var isClosed = false
            var index = 0
            override fun lines(): Sequence<String> {
                return sequence {
                    while (index < file.linesToRead.size) {
                        yield(file.linesToRead[index])
                        index++
                    }
                }
            }

            override fun close() {
                isClosed = true
            }
        }

        override fun toFileWriter(): FileWriter {
            val writer = MockFileWriter(this)
            writersCreated.add(writer)
            return writer
        }

        override fun toFileReader(): FileReader {
            val reader = MockFileReader(this)
            readersCreated.add(reader)
            return reader
        }

        override fun delete() {
            isDeleted = true
        }
    }

    override fun createTempFile(directory: Path, prefix: String, suffix: String): LocalFile {
        return MockLocalFile()
    }
}
