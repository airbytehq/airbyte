/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.test.fixtures.legacy

import com.google.common.base.Charsets
import java.io.*
import java.nio.charset.StandardCharsets
import java.nio.file.Files
import java.nio.file.Path
import java.nio.file.Paths
import java.util.*
import org.apache.commons.io.input.ReversedLinesFileReader

object IOs {
    @JvmStatic
    fun writeFile(path: Path, fileName: String?, contents: String?): Path {
        val filePath = path.resolve(fileName)
        return writeFile(filePath, contents)
    }

    @JvmStatic
    fun writeFile(filePath: Path, contents: ByteArray): Path {
        try {
            Files.write(filePath, contents)
            return filePath
        } catch (e: IOException) {
            throw RuntimeException(e)
        }
    }

    @JvmStatic
    fun writeFile(filePath: Path, contents: String?): Path {
        try {
            Files.writeString(filePath, contents, StandardCharsets.UTF_8)
            return filePath
        } catch (e: IOException) {
            throw RuntimeException(e)
        }
    }

    /**
     * Writes a file to a random directory in the /tmp folder. Useful as a staging group for test
     * resources.
     */
    @JvmStatic
    fun writeFileToRandomTmpDir(filename: String?, contents: String?): String {
        val source = Paths.get("/tmp", UUID.randomUUID().toString())
        try {
            val tmpFile = source.resolve(filename)
            Files.deleteIfExists(tmpFile)
            Files.createDirectory(source)
            writeFile(tmpFile, contents)
            return tmpFile.toString()
        } catch (e: IOException) {
            throw RuntimeException(e)
        }
    }

    @JvmStatic
    fun readFile(path: Path, fileName: String?): String {
        return readFile(path.resolve(fileName))
    }

    @JvmStatic
    fun readFile(fullpath: Path?): String {
        try {
            return Files.readString(fullpath, StandardCharsets.UTF_8)
        } catch (e: IOException) {
            throw RuntimeException(e)
        }
    }

    @Throws(IOException::class)
    @JvmStatic
    fun getTail(numLines: Int, path: Path?): List<String> {
        if (path == null) {
            return emptyList<String>()
        }

        val file = path.toFile()
        if (!file.exists()) {
            return emptyList<String>()
        }

        ReversedLinesFileReader.Builder().setFile(file).setCharset(Charsets.UTF_8).get().use {
            fileReader ->
            val lines: MutableList<String> = ArrayList()
            var line = fileReader.readLine()
            while (line != null && lines.size < numLines) {
                lines.add(line)
                line = fileReader.readLine()
            }

            Collections.reverse(lines)
            return lines
        }
    }

    @JvmStatic
    fun inputStream(path: Path): InputStream {
        try {
            return Files.newInputStream(path)
        } catch (e: IOException) {
            throw RuntimeException(e)
        }
    }

    @JvmStatic
    fun silentClose(closeable: Closeable) {
        try {
            closeable.close()
        } catch (e: IOException) {
            throw RuntimeException(e)
        }
    }

    @JvmStatic
    fun newBufferedReader(inputStream: InputStream): BufferedReader {
        return BufferedReader(InputStreamReader(inputStream, StandardCharsets.UTF_8))
    }
}
