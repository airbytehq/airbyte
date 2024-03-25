/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.commons.io

import com.google.common.collect.Iterables
import java.io.*
import java.nio.charset.StandardCharsets
import java.nio.file.Files
import java.nio.file.Path
import org.apache.commons.lang3.RandomStringUtils
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test
import org.mockito.Mockito

internal class IOsTest {
    @Test
    @Throws(IOException::class)
    fun testReadWrite() {
        val path = Files.createTempDirectory("tmp")

        val filePath = IOs.writeFile(path, FILE, ABC)

        Assertions.assertEquals(path.resolve(FILE), filePath)
        Assertions.assertEquals(ABC, IOs.readFile(path, FILE))
        Assertions.assertEquals(ABC, IOs.readFile(path.resolve(FILE)))
    }

    @Test
    @Throws(IOException::class)
    fun testWriteBytes() {
        val path = Files.createTempDirectory("tmp")

        val filePath = IOs.writeFile(path.resolve(FILE), ABC.toByteArray(StandardCharsets.UTF_8))

        Assertions.assertEquals(path.resolve(FILE), filePath)
        Assertions.assertEquals(ABC, IOs.readFile(path, FILE))
    }

    @Test
    @Throws(IOException::class)
    fun testWriteFileToRandomDir() {
        val contents = "something to remember"
        val tmpFilePath = IOs.writeFileToRandomTmpDir("file.txt", contents)
        Assertions.assertEquals(contents, Files.readString(Path.of(tmpFilePath)))
    }

    @Test
    @Throws(IOException::class)
    fun testGetTailDoesNotExist() {
        val tail = IOs.getTail(100, Path.of(RandomStringUtils.randomAlphanumeric(100)))
        Assertions.assertEquals(emptyList<Any>(), tail)
    }

    @Test
    @Throws(IOException::class)
    fun testGetTailExists() {
        val stdoutFile = Files.createTempFile("job-history-handler-test", "stdout")

        val head = listOf("line1", "line2", "line3", "line4")

        val expectedTail = listOf("line5", "line6", "line7", "line8")

        val writer: Writer =
            BufferedWriter(FileWriter(stdoutFile.toString(), StandardCharsets.UTF_8, true))

        for (line in Iterables.concat(head, expectedTail)) {
            writer.write(line + "\n")
        }

        writer.close()

        val tail = IOs.getTail(expectedTail.size, stdoutFile)
        Assertions.assertEquals(expectedTail, tail)
    }

    @Test
    fun testInputStream() {
        Assertions.assertThrows(RuntimeException::class.java) {
            IOs.inputStream(Path.of("idontexist"))
        }
    }

    @Test
    @Throws(IOException::class)
    fun testSilentClose() {
        val closeable = Mockito.mock(Closeable::class.java)

        Assertions.assertDoesNotThrow { IOs.silentClose(closeable) }

        Mockito.doThrow(IOException()).`when`(closeable).close()
        Assertions.assertThrows(RuntimeException::class.java) { IOs.silentClose(closeable) }
    }

    companion object {
        private const val ABC = "abc"
        private const val FILE = "file"
    }
}
