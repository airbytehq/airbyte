/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.write

import io.airbyte.cdk.load.command.Append
import io.airbyte.cdk.load.command.Dedupe
import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.command.NamespaceMapper
import io.airbyte.cdk.load.data.FieldType
import io.airbyte.cdk.load.data.ObjectType
import io.airbyte.cdk.load.data.ObjectTypeWithoutSchema
import io.airbyte.cdk.load.data.json.toAirbyteValue
import io.airbyte.cdk.load.message.DestinationFile
import io.airbyte.cdk.load.message.InputFile
import io.airbyte.cdk.load.message.InputRecord
import io.airbyte.cdk.load.state.CheckpointId
import io.airbyte.cdk.load.test.util.destination_process.DestinationProcess
import io.airbyte.cdk.load.util.CloseableCoroutine
import io.airbyte.cdk.load.util.serializeToString
import io.airbyte.cdk.load.util.use
import io.airbyte.protocol.models.Jsons
import io.airbyte.protocol.models.v0.AirbyteRecordMessageFileReference
import io.github.oshai.kotlinlogging.KotlinLogging
import java.nio.file.Path
import java.security.SecureRandom
import kotlin.random.Random

/**
 * Single stream performance test.
 *
 * This performance scenario will insert [recordsToInsert] records are generated from the [idColumn]
 * and [columns] parameters. Records are the same except for the id which will be automatically
 * incremented. [dedup] controls whether the insert mode is `Append` or `Dedupe`. [duplicateChance]
 * if non 0 will insert random duplicates of records.
 */
class SingleStreamInsert(
    private val idColumn: NamedField,
    private val columns: List<NamedField>,
    private val recordsToInsert: Long,
    private val dedup: Boolean = false,
    duplicateChance: Double = 0.0,
    randomizedNamespace: String,
    streamName: String,
    generationId: Long = 0,
    minGenerationId: Long = 0,
) : PerformanceTestScenario {

    init {
        assert(duplicateChance in 0.0..1.0)
    }

    private val stream = run {
        val importType =
            if (!dedup) Append
            else
                Dedupe(
                    primaryKey = listOf(listOf(idColumn.name)),
                    cursor = listOf(idColumn.name),
                )
        val schema =
            (listOf(idColumn) + columns).map {
                Pair(it.name, FieldType(type = it.type, nullable = true))
            }

        DestinationStream(
            unmappedNamespace = randomizedNamespace,
            unmappedName = streamName,
            importType = importType,
            schema = ObjectType(linkedMapOf(*schema.toTypedArray())),
            generationId = generationId,
            minimumGenerationId = minGenerationId,
            syncId = 1,
            namespaceMapper = NamespaceMapper()
        )
    }

    private val random = SecureRandom()
    private val randomThreshold: Int =
        if (duplicateChance > 0.0) ((duplicateChance % 1.0) * 100).toInt() else 0

    private var recordCount: Long = 0
    private var byteCount: Long = 0

    override val catalog = DestinationCatalog(listOf(stream))

    class RecordWriter(
        indexColumn: NamedField,
        columns: List<NamedField>,
        stream: DestinationStream,
        private val destination: DestinationProcess,
        private val recordBufferSize: Long = 1,
        private val checkpointId: CheckpointId? = null,
    ) : CloseableCoroutine {
        private val baseRecord = run {
            val data = (listOf(indexColumn) + columns).associate { Pair(it.name, it.sample) }
            InputRecord(
                stream = stream,
                data = Jsons.serialize(data),
                emittedAtMs = System.currentTimeMillis(),
                checkpointId = checkpointId
            )
        }
        private val messageParts =
            Jsons.serialize(baseRecord.asProtocolMessage()).split(indexColumn.sample.toString())
        private val baseMessageSize = messageParts.sumOf { it.length }

        private val sb = StringBuilder()

        var recordWritten: Long = 0
        var bytesWritten: Long = 0

        suspend fun write(id: Long) {
            sb.append(messageParts[0])
            sb.append(id)
            sb.append(messageParts[1])
            sb.appendLine()

            if (recordWritten % recordBufferSize == 0L) {
                flush()
            }

            recordWritten += 1
            bytesWritten += baseMessageSize + id.length()
        }

        private suspend fun flush() {
            if (sb.isNotEmpty()) {
                destination.sendMessage(sb.toString())
                sb.clear()
            }
        }

        override suspend fun close() {
            flush()
        }
    }

    override suspend fun send(destination: DestinationProcess) {
        RecordWriter(
                indexColumn = idColumn,
                columns = columns,
                stream = stream,
                destination = destination,
                recordBufferSize = 10,
                checkpointId = checkpointKeyForMedium(destination.dataChannelMedium)?.checkpointId,
            )
            .use { writer ->
                (1..recordsToInsert).forEach {
                    writer.write(it)
                    if (randomThreshold > 0 && random.nextInt(0, 100) <= randomThreshold) {
                        writer.write(it)
                    }
                }
                recordCount = writer.recordWritten
                byteCount = writer.bytesWritten
            }
    }

    override fun getSummary() =
        PerformanceTestScenario.Summary(
            recordCount,
            byteCount,
            expectedRecordsCount = if (dedup) recordsToInsert else recordCount,
        )
}

class SingleStreamFileTransfer(
    private val randomizedNamespace: String,
    private val streamName: String,
    private val numFiles: Int,
    private val fileSizeMb: Int,
    private val stagingDirectory: Path,
    private val seed: Long = 8656931613L
) : PerformanceTestScenario {
    private val log = KotlinLogging.logger {}

    private val stream =
        DestinationStream(
            unmappedNamespace = randomizedNamespace,
            unmappedName = streamName,
            importType = Append,
            schema = ObjectType(linkedMapOf()),
            generationId = 1,
            minimumGenerationId = 0,
            syncId = 1,
            namespaceMapper = NamespaceMapper()
        )

    override val catalog: DestinationCatalog =
        DestinationCatalog(
            listOf(
                DestinationStream(
                    unmappedNamespace = randomizedNamespace,
                    unmappedName = streamName,
                    importType = Append,
                    schema = ObjectTypeWithoutSchema,
                    generationId = 1,
                    minimumGenerationId = 1,
                    syncId = 101,
                    namespaceMapper = NamespaceMapper(),
                )
            )
        )

    private fun makeFileName(index: Long): String =
        "test_file__${randomizedNamespace}__${streamName}__$index.txt"

    fun setup() {
        // TODO: Maybe make these files different sizes?
        val prng = Random(seed)
        val randomMegabyte = ByteArray(1024 * 1024) { prng.nextInt().toByte() }
        repeat(numFiles) {
            val file = stagingDirectory.resolve(makeFileName(it.toLong()))
            log.info { "Creating file $file with size ${fileSizeMb}mb" }
            val outputStream = file.toFile().outputStream()
            repeat(fileSizeMb) { outputStream.write(randomMegabyte) }
            outputStream.close()
        }
    }

    override suspend fun send(destination: DestinationProcess) {
        repeat(numFiles) {
            val fileName = makeFileName(it.toLong())
            val message =
                DestinationFile(
                    stream,
                    System.currentTimeMillis(),
                    DestinationFile.AirbyteRecordMessageFile(
                        fileUrl = stagingDirectory.resolve(fileName).toString(),
                        fileRelativePath = fileName,
                        bytes = fileSizeMb * 1024 * 1024L,
                        modified = System.currentTimeMillis(),
                        sourceFileUrl = fileName,
                    )
                )
            destination.sendMessage(InputFile(message))
        }
    }

    override fun getSummary(): PerformanceTestScenario.Summary =
        PerformanceTestScenario.Summary(
            records = numFiles.toLong(),
            size = numFiles * fileSizeMb * 1024 * 1024L,
            expectedRecordsCount = numFiles.toLong()
        )
}

class SingleStreamFileAndMetadataTransfer(
    private val randomizedNamespace: String,
    private val streamName: String,
    private val numFiles: Int,
    private val fileSizeMb: Int,
    private val stagingDirectory: Path,
    private val seed: Long = 8656931613L
) : PerformanceTestScenario {
    private val log = KotlinLogging.logger {}

    private val stream =
        DestinationStream(
            unmappedNamespace = randomizedNamespace,
            unmappedName = streamName,
            importType = Append,
            schema = ObjectType(linkedMapOf()),
            generationId = 1,
            minimumGenerationId = 0,
            syncId = 1,
            includeFiles = true,
            namespaceMapper = NamespaceMapper()
        )

    override val catalog: DestinationCatalog =
        DestinationCatalog(
            listOf(
                DestinationStream(
                    unmappedNamespace = randomizedNamespace,
                    unmappedName = streamName,
                    importType = Append,
                    schema = ObjectTypeWithoutSchema,
                    generationId = 1,
                    minimumGenerationId = 1,
                    syncId = 101,
                    includeFiles = true,
                    namespaceMapper = NamespaceMapper()
                )
            )
        )

    private fun makeFileName(index: Long): String =
        "test_file__${randomizedNamespace}__${streamName}__$index.txt"

    fun setup() {
        // TODO: Maybe make these files different sizes?
        val prng = Random(seed)
        val randomMegabyte = ByteArray(1024 * 1024) { prng.nextInt().toByte() }
        repeat(numFiles) {
            val file = stagingDirectory.resolve(makeFileName(it.toLong()))
            log.info { "Creating file $file with size ${fileSizeMb}mb" }
            val outputStream = file.toFile().outputStream()
            repeat(fileSizeMb) { outputStream.write(randomMegabyte) }
            outputStream.close()
        }
    }

    override suspend fun send(destination: DestinationProcess) {
        repeat(numFiles) {
            val fileName = makeFileName(it.toLong())

            val file =
                AirbyteRecordMessageFileReference()
                    .withFileSizeBytes(fileSizeMb * 1024 * 1024L)
                    .withStagingFileUrl(stagingDirectory.resolve(fileName).toString())
                    .withSourceFileRelativePath(fileName)

            val dataStr =
                """
                {
                      "id": 12138758717583,
                      "url": "https://d3v-airbyte.zendesk.com/api/v2/help_center/articles/attachments/12138758717583",
                      "article_id": 12138789487375,
                      "display_file_name": "DALL·E 2024-11-19 10.07.37 - A cartoon-style robot with a metallic, retro-futuristic design, holding a smoking cigar in one hand. The robot has a humorous, relaxed expression, wit (1).webp",
                      "file_name": "DALL·E 2024-11-19 10.07.37 - A cartoon-style robot with a metallic, retro-futuristic design, holding a smoking cigar in one hand. The robot has a humorous, relaxed expression, wit (1).webp",
                      "locale": "en-us",
                      "content_url": "https://d3v-airbyte.zendesk.com/hc/article_attachments/12138758717583",
                      "relative_path": "/hc/article_attachments/12138758717583",
                      "content_type": "image/webp",
                      "size": 109284,
                      "inline": true,
                      "created_at": "2025-03-11T23:33:57Z",
                      "updated_at": "2025-03-11T23:33:57Z"
                    }
            """.trimIndent()

            val msg =
                InputRecord(
                    stream = stream,
                    data = Jsons.deserialize(dataStr).toAirbyteValue(),
                    emittedAtMs = System.currentTimeMillis(),
                    fileReference = file,
                    meta = null,
                    serialized = dataStr,
                    checkpointId =
                        checkpointKeyForMedium(destination.dataChannelMedium)?.checkpointId
                )

            destination.sendMessage(msg)
        }
    }

    override fun getSummary(): PerformanceTestScenario.Summary =
        PerformanceTestScenario.Summary(
            records = numFiles.toLong(),
            size = numFiles * fileSizeMb * 1024 * 1024L,
            expectedRecordsCount = numFiles.toLong()
        )
}

/**
 * This was a quick hack and doesn't yet support dedupe or interleaving. Note that the input records
 * are all identical, which would have to be corrected before supporting the former.
 */
class MultiStreamInsert(
    private val numStreams: Int,
    private val streamNamePrefix: String,
    private val idColumn: NamedField,
    private val columns: List<NamedField>,
    private val recordsToInsertPerStream: Long,
    randomizedNamespace: String,
    generationId: Long = 0,
    minGenerationId: Long = 0,
) : PerformanceTestScenario {

    private val streams = run {
        val importType = Append
        val schema =
            (listOf(idColumn) + columns).map {
                Pair(it.name, FieldType(type = it.type, nullable = true))
            }

        (0 until numStreams).map {
            DestinationStream(
                unmappedNamespace = randomizedNamespace,
                unmappedName = "${streamNamePrefix}__$it",
                importType = importType,
                schema = ObjectType(linkedMapOf(*schema.toTypedArray())),
                generationId = generationId,
                minimumGenerationId = minGenerationId,
                syncId = 1,
                namespaceMapper = NamespaceMapper()
            )
        }
    }

    private var recordCount: Long = 0
    private var byteCount: Long = 0

    override val catalog = DestinationCatalog(streams)

    override suspend fun send(destination: DestinationProcess) {
        streams.forEach { stream ->
            val inputRecord =
                InputRecord(
                    stream = stream,
                    data =
                        Jsons.serialize(
                            (listOf(idColumn) + columns).associate { Pair(it.name, it.sample) }
                        ),
                    emittedAtMs = System.currentTimeMillis(),
                    checkpointId =
                        checkpointKeyForMedium(destination.dataChannelMedium)?.checkpointId
                )
            val jsonString = inputRecord.serializeToString()
            val size = jsonString.length.toLong()

            (0 until recordsToInsertPerStream).forEach { _ ->
                destination.sendMessage(inputRecord)
                recordCount++
                byteCount += size
            }
        }
    }

    override fun getSummary() =
        PerformanceTestScenario.Summary(
            recordCount,
            byteCount,
            expectedRecordsCount = recordsToInsertPerStream * streams.size
        )
}

private fun Long.length(): Long =
    if (this <= 99999) {
        if (this <= 99) {
            if (this <= 9) {
                1
            } else {
                2
            }
        } else {
            if (this <= 999) {
                3
            } else {
                if (this <= 9999) {
                    4
                } else {
                    5
                }
            }
        }
    } else {
        if (this <= 9999999) {
            if (this <= 999999) {
                6
            } else {
                7
            }
        } else {
            if (this <= 99999999) {
                8
            } else {
                if (this <= 999999999) {
                    9
                } else {
                    10
                }
            }
        }
    }
