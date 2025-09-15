/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.debezium.internals

import com.fasterxml.jackson.databind.JsonNode
import com.google.common.annotations.VisibleForTesting
import io.airbyte.commons.json.Jsons
import io.debezium.document.DocumentReader
import io.debezium.document.DocumentWriter
import io.github.oshai.kotlinlogging.KotlinLogging
import java.io.*
import java.nio.charset.Charset
import java.nio.charset.StandardCharsets
import java.nio.file.FileAlreadyExistsException
import java.nio.file.Files
import java.nio.file.Path
import java.nio.file.StandardOpenOption
import java.util.*
import java.util.zip.GZIPInputStream
import java.util.zip.GZIPOutputStream
import org.apache.commons.io.FileUtils

private val LOGGER = KotlinLogging.logger {}
/**
 * The purpose of this class is : to , 1. Read the contents of the file [.path] which contains the
 * schema history at the end of the sync so that it can be saved in state for future syncs. Check
 * [.read] 2. Write the saved content back to the file [.path] at the beginning of the sync so that
 * debezium can function smoothly. Check persist(Optional&lt;JsonNode&gt;).
 */
class AirbyteSchemaHistoryStorage(
    private val path: Path,
    private val compressSchemaHistoryForState: Boolean
) {
    private val reader: DocumentReader = DocumentReader.defaultReader()
    private val writer: DocumentWriter = DocumentWriter.defaultWriter()

    data class SchemaHistory<T>(val schema: T, val isCompressed: Boolean)

    fun read(): SchemaHistory<String> {
        val fileSizeMB = path.toFile().length().toDouble() / (ONE_MB)
        if ((fileSizeMB > SIZE_LIMIT_TO_COMPRESS_MB) && compressSchemaHistoryForState) {
            LOGGER.info {
                "File Size $fileSizeMB MB is greater than the size limit of $SIZE_LIMIT_TO_COMPRESS_MB MB, compressing the content of the file."
            }
            val schemaHistory = readCompressed()
            val compressedSizeMB = calculateSizeOfStringInMB(schemaHistory)
            if (fileSizeMB > compressedSizeMB) {
                LOGGER.info { "Content Size post compression is $compressedSizeMB MB " }
            } else {
                throw RuntimeException(
                    "Compressing increased the size of the content. Size before compression ${fileSizeMB}MB " +
                        ", after compression ${compressedSizeMB}MB"
                )
            }
            return SchemaHistory(schemaHistory, true)
        }
        if (compressSchemaHistoryForState) {
            LOGGER.info {
                "File Size $fileSizeMB MB is less than the size limit of $SIZE_LIMIT_TO_COMPRESS_MB MB, reading the content of the file without compression."
            }
        } else {
            LOGGER.info { "File Size $fileSizeMB MB." }
        }
        val schemaHistory = readUncompressed()
        return SchemaHistory(schemaHistory, false)
    }

    @VisibleForTesting
    fun readUncompressed(): String {
        val fileAsString = StringBuilder()
        try {
            for (line in Files.readAllLines(path, UTF8)) {
                if (line != null && !line.isEmpty()) {
                    val record = reader.read(line)
                    val recordAsString = writer.write(record)
                    fileAsString.append(recordAsString)
                    fileAsString.append(System.lineSeparator())
                }
            }
            return fileAsString.toString()
        } catch (e: IOException) {
            throw RuntimeException(e)
        }
    }

    private fun readCompressed(): String {
        val lineSeparator = System.lineSeparator()
        val compressedStream = ByteArrayOutputStream()
        try {
            GZIPOutputStream(compressedStream).use { gzipOutputStream ->
                Files.newBufferedReader(path, UTF8).use { bufferedReader ->
                    while (true) {
                        val line = bufferedReader.readLine() ?: break

                        if (!line.isEmpty()) {
                            val record = reader.read(line)
                            val recordAsString = writer.write(record)
                            gzipOutputStream.write(
                                recordAsString.toByteArray(StandardCharsets.UTF_8)
                            )
                            gzipOutputStream.write(
                                lineSeparator.toByteArray(StandardCharsets.UTF_8)
                            )
                        }
                    }
                }
            }
        } catch (e: IOException) {
            throw RuntimeException(e)
        }
        return Jsons.serialize(compressedStream.toByteArray())
    }

    private fun makeSureFileExists() {
        try {
            // Make sure the file exists ...
            if (!Files.exists(path)) {
                // Create parent directories if we have them ...
                if (path.parent != null) {
                    Files.createDirectories(path.parent)
                }
                try {
                    Files.createFile(path)
                } catch (e: FileAlreadyExistsException) {
                    // do nothing
                }
            }
        } catch (e: IOException) {
            throw IllegalStateException(
                "Unable to check or create history file at " + path + ": " + e.message,
                e
            )
        }
    }

    private fun persist(schemaHistory: SchemaHistory<Optional<JsonNode>>?) {
        if (schemaHistory!!.schema.isEmpty) {
            return
        }
        val fileAsString = Jsons.`object`(schemaHistory.schema.get(), String::class.java)

        if (fileAsString.isNullOrEmpty()) {
            return
        }

        FileUtils.deleteQuietly(path.toFile())
        makeSureFileExists()
        if (schemaHistory.isCompressed) {
            writeCompressedStringToFile(fileAsString)
        } else {
            writeToFile(fileAsString)
        }
    }

    /**
     * @param fileAsString Represents the contents of the file saved in state from previous syncs
     */
    private fun writeToFile(fileAsString: String) {
        try {
            val split =
                fileAsString
                    .split(System.lineSeparator().toRegex())
                    .dropLastWhile { it.isEmpty() }
                    .toTypedArray()
            for (element in split) {
                val read = reader.read(element)
                val line = writer.write(read)

                Files.newBufferedWriter(path, StandardOpenOption.APPEND).use { historyWriter ->
                    try {
                        historyWriter.append(line)
                        historyWriter.newLine()
                    } catch (e: IOException) {
                        throw RuntimeException(e)
                    }
                }
            }
        } catch (e: IOException) {
            throw RuntimeException(e)
        }
    }

    private fun writeCompressedStringToFile(compressedString: String) {
        try {
            ByteArrayInputStream(Jsons.deserialize(compressedString, ByteArray::class.java)).use {
                inputStream ->
                GZIPInputStream(inputStream).use { gzipInputStream ->
                    FileOutputStream(path.toFile()).use { fileOutputStream ->
                        val buffer = ByteArray(1024)
                        var bytesRead: Int
                        while ((gzipInputStream.read(buffer).also { bytesRead = it }) != -1) {
                            fileOutputStream.write(buffer, 0, bytesRead)
                        }
                    }
                }
            }
        } catch (e: IOException) {
            throw RuntimeException(e)
        }
    }

    fun setDebeziumProperties(props: Properties) {
        // https://debezium.io/documentation/reference/2.2/operations/debezium-server.html#debezium-source-database-history-class
        // https://debezium.io/documentation/reference/development/engine.html#_in_the_code
        // As mentioned in the documents above, debezium connector for MySQL needs to track the
        // schema
        // changes. If we don't do this, we can't fetch records for the table.
        props.setProperty(
            "schema.history.internal",
            "io.debezium.storage.file.history.FileSchemaHistory"
        )
        props.setProperty("schema.history.internal.file.filename", path.toString())
        props.setProperty("schema.history.internal.store.only.captured.databases.ddl", "true")
    }

    companion object {
        private const val SIZE_LIMIT_TO_COMPRESS_MB: Long = 1
        const val ONE_MB: Int = 1024 * 1024
        private val UTF8: Charset = StandardCharsets.UTF_8

        @VisibleForTesting
        fun calculateSizeOfStringInMB(string: String): Double {
            return string.toByteArray(StandardCharsets.UTF_8).size.toDouble() / (ONE_MB)
        }

        @JvmStatic
        fun initializeDBHistory(
            schemaHistory: SchemaHistory<Optional<JsonNode>>?,
            compressSchemaHistoryForState: Boolean
        ): AirbyteSchemaHistoryStorage {
            val dbHistoryWorkingDir: Path
            try {
                dbHistoryWorkingDir = Files.createTempDirectory(Path.of("/tmp"), "cdc-db-history")
            } catch (e: IOException) {
                throw RuntimeException(e)
            }
            val dbHistoryFilePath = dbHistoryWorkingDir.resolve("dbhistory.dat")

            val schemaHistoryManager =
                AirbyteSchemaHistoryStorage(dbHistoryFilePath, compressSchemaHistoryForState)
            schemaHistoryManager.persist(schemaHistory)
            return schemaHistoryManager
        }
    }
}
