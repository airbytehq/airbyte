/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.bigquery.copy

import com.sun.net.httpserver.HttpExchange
import com.sun.net.httpserver.HttpServer
import java.io.BufferedInputStream
import java.io.InputStream
import java.net.InetSocketAddress
import java.net.URI
import java.nio.file.Files
import java.nio.file.Path
import java.security.MessageDigest
import java.util.concurrent.ConcurrentHashMap
import java.util.concurrent.CountDownLatch
import java.util.concurrent.Executors
import java.util.concurrent.TimeUnit
import java.util.concurrent.atomic.AtomicInteger
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.async
import kotlinx.coroutines.cancelAndJoin
import kotlinx.coroutines.runBlocking
import kotlinx.coroutines.withContext
import kotlinx.coroutines.withTimeout
import org.junit.jupiter.api.Assertions.*
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.io.TempDir
import software.amazon.awssdk.auth.credentials.AwsBasicCredentials
import software.amazon.awssdk.auth.credentials.StaticCredentialsProvider
import software.amazon.awssdk.regions.Region

/** Real SDK, real Netty and a local S3 protocol fixture. No AWS account or credentials are used. */
class S3ArchiveUploaderMultipartTest {
    @TempDir lateinit var directory: Path

    @Test
    fun `real multipart retries identical part bytes and waits for complete upload`() =
        runBlocking {
            FakeS3(failPermanently = false).use { server ->
                val path = largeFile()
                val expected = partDigests(path)
                val uploader = uploader(server)
                try {
                    val operation = async {
                        uploader.upload(
                            path,
                            "fusion/batch.csv.gz",
                            "application/gzip",
                            mapOf("batch-id" to "test"),
                        )
                    }
                    withContext(Dispatchers.IO) {
                        assertTrue(server.completing.await(30, TimeUnit.SECONDS))
                    }
                    assertFalse(operation.isCompleted)
                    assertEquals(expected.keys, server.digests.keys)
                    expected.forEach { (part, digest) ->
                        server.digests.getValue(part).forEach { actual ->
                            assertArrayEquals(digest, actual)
                        }
                    }
                    assertEquals(2, server.attempts.getValue(2).get())
                    assertEquals(5, server.partsInCompletion.get())
                    assertEquals("application/gzip", server.contentType)
                    assertEquals("test", server.batchId)
                    server.allowCompletion.countDown()
                    operation.await()
                    assertEquals(0, server.aborts.get())
                    assertEquals(1, server.creates.get())
                    Files.delete(path)
                } finally {
                    server.allowCompletion.countDown()
                    uploader.close()
                }
            }
        }

    @Test
    fun `real multipart retries when server rejects a partially consumed part`() = runBlocking {
        FakeS3(failPermanently = false, failBeforeConsumption = true).use { server ->
            val path = largeFile()
            val expected = partDigests(path)
            val uploader = uploader(server)
            server.allowCompletion.countDown()
            try {
                uploader.upload(path, "fusion/batch.csv.gz", "application/gzip")
                assertEquals(2, server.attempts.getValue(2).get())
                expected.forEach { (part, digest) ->
                    server.digests.getValue(part).forEach { actual ->
                        assertArrayEquals(digest, actual)
                    }
                }
                assertEquals(5, server.partsInCompletion.get())
            } finally {
                uploader.close()
            }
        }
    }

    @Test
    fun `real multipart terminal part failure aborts and never completes object`() = runBlocking {
        FakeS3(failPermanently = true).use { server ->
            val uploader = uploader(server)
            try {
                val failure =
                    runCatching {
                            uploader.upload(largeFile(), "fusion/batch.csv.gz", "application/gzip")
                        }
                        .exceptionOrNull()
                assertNotNull(failure)
                assertFalse(failure is ArchiveReaderStillActiveException)
                withContext(Dispatchers.IO) {
                    assertTrue(server.aborted.await(10, TimeUnit.SECONDS))
                }
                assertEquals(1, server.aborts.get())
                assertEquals(0, server.partsInCompletion.get())
            } finally {
                uploader.close()
            }
        }
    }

    @Test
    fun `large multipart upload bounds outstanding parts while S3 applies backpressure`() =
        runBlocking {
            FakeS3(failPermanently = false, holdParts = true, failOnce = false).use { server ->
                val path = directory.resolve("large.jsonl")
                // Seventeen parts exceed the 16-connection HTTP pool. The old 65 MiB fixture only
                // produced five parts and could not exercise connection acquisition starvation.
                val line = "{\"data\":\"${"x".repeat(8179)}\"}\n".toByteArray()
                assertEquals(8191, line.size)
                Files.newOutputStream(path).buffered().use { output ->
                    repeat((16 * S3ArchiveUploader.PART_SIZE / line.size + 1).toInt()) {
                        output.write(line)
                    }
                }
                val expected = partDigests(path)
                assertEquals(17, expected.size)
                val uploader = uploader(server)
                server.allowCompletion.countDown()
                val operation = async {
                    uploader.upload(path, "fusion/large.jsonl", "application/x-ndjson")
                }
                try {
                    withContext(Dispatchers.IO) {
                        assertTrue(server.twoPartsStarted.await(10, TimeUnit.SECONDS))
                        assertFalse(
                            server.thirdPartStarted.await(1, TimeUnit.SECONDS),
                            "More than two parts were scheduled before any part completed",
                        )
                    }
                    assertFalse(operation.isCompleted)
                    server.allowParts.countDown()
                    withTimeout(30_000) { operation.await() }
                    assertEquals(17, server.partsInCompletion.get())
                    assertEquals(17, server.attempts.size)
                    assertTrue(server.attempts.values.all { it.get() == 1 })
                    expected.forEach { (part, hash) ->
                        assertArrayEquals(hash, server.digests.getValue(part).single())
                    }
                    assertEquals(0, server.aborts.get())
                    Files.delete(path)
                } finally {
                    server.allowParts.countDown()
                    operation.cancelAndJoin()
                    uploader.close()
                }
            }
        }

    @Test
    fun `real streaming multipart uploads during append and completes on seal before finish`() =
        runBlocking {
            FakeS3(failPermanently = false, holdParts = true, failBeforeConsumption = true).use {
                server ->
                val uploader = uploader(server)
                val upload =
                    uploader.startStreaming(
                        "fusion/streaming.jsonl",
                        "application/x-ndjson",
                        mapOf("batch-id" to "streaming"),
                        directory
                    )
                val first = ByteArray(S3ArchiveUploader.PART_SIZE.toInt()) { (it % 127).toByte() }
                val second = ByteArray(first.size) { (it % 113).toByte() }
                val last = "last bytes\n".toByteArray()
                try {
                    upload.append(first)
                    upload.append(second)
                    withContext(Dispatchers.IO) {
                        assertTrue(server.twoPartsStarted.await(10, TimeUnit.SECONDS))
                        assertFalse(server.thirdPartStarted.await(100, TimeUnit.MILLISECONDS))
                    }
                    assertEquals(0, server.partsInCompletion.get())
                    server.allowParts.countDown()
                    upload.append(last)
                    upload.seal()
                    withContext(Dispatchers.IO) {
                        assertTrue(server.completing.await(10, TimeUnit.SECONDS))
                    }
                    assertEquals(3, server.partsInCompletion.get())
                    assertEquals(3, server.checksumsInCompletion.get())
                    assertEquals("CRC32", server.checksumAlgorithm)
                    assertEquals("COMPOSITE", server.checksumType)
                    assertEquals(
                        mapOf(1 to "CRC32", 2 to "CRC32", 3 to "CRC32"),
                        server.partChecksumAlgorithms
                    )
                    assertEquals("application/x-ndjson", server.contentType)
                    assertEquals("streaming", server.batchId)
                    val finished = async { upload.finish() }
                    kotlinx.coroutines.yield()
                    assertFalse(finished.isCompleted)
                    server.allowCompletion.countDown()
                    withTimeout(10_000) { finished.await() }
                    listOf(first, second, last).forEachIndexed { index, bytes ->
                        assertArrayEquals(
                            MessageDigest.getInstance("SHA-256").digest(bytes),
                            server.digests.getValue(index + 1).single()
                        )
                    }
                    assertEquals(0, Files.list(directory).use { it.count() })
                    assertEquals(2, server.attempts.getValue(2).get())
                    assertEquals(0, server.aborts.get())
                } finally {
                    server.allowParts.countDown()
                    server.allowCompletion.countDown()
                    upload.close()
                    uploader.close()
                }
            }
        }

    private fun uploader(server: FakeS3): S3ArchiveUploader {
        val credentials =
            StaticCredentialsProvider.create(AwsBasicCredentials.create("test", "test"))
        val client =
            S3ArchiveUploader.s3ClientBuilder()
                .region(Region.US_EAST_1)
                .credentialsProvider(credentials)
                .endpointOverride(URI.create("http://127.0.0.1:${server.port}"))
                .forcePathStyle(true)
                .build()
        return S3ArchiveUploader("archive", client, credentials, listOf(client))
    }

    private fun largeFile(): Path {
        val path = directory.resolve("large.csv.gz")
        val block = ByteArray(8192) { (it * 31).toByte() }
        Files.newOutputStream(path).use { output ->
            repeat(65 * 128) { index ->
                // Distinguish equal-sized parts so a retry at the wrong offset cannot pass the
                // digest check.
                block[0] = (index / (16 * 128)).toByte()
                output.write(block)
            }
        }
        return path
    }

    private fun partDigests(path: Path): Map<Int, ByteArray> {
        val parts = mutableMapOf<Int, ByteArray>()
        Files.newInputStream(path).use { input ->
            var remaining = Files.size(path)
            while (remaining > 0) {
                val size = minOf(remaining, S3ArchiveUploader.PART_SIZE)
                parts[parts.size + 1] = digest(input, size)
                remaining -= size
            }
        }
        return parts
    }

    private class FakeS3(
        private val failPermanently: Boolean,
        private val failBeforeConsumption: Boolean = false,
        private val holdParts: Boolean = false,
        private val failOnce: Boolean = true,
    ) : AutoCloseable {
        private val workers = Executors.newFixedThreadPool(16)
        private val server = HttpServer.create(InetSocketAddress("127.0.0.1", 0), 0)
        val port: Int
            get() = server.address.port

        val digests = ConcurrentHashMap<Int, MutableList<ByteArray>>()
        val attempts = ConcurrentHashMap<Int, AtomicInteger>()
        val twoPartsStarted = CountDownLatch(2)
        val thirdPartStarted = CountDownLatch(3)
        val allowParts = CountDownLatch(if (holdParts) 1 else 0)
        val creates = AtomicInteger()
        val aborts = AtomicInteger()
        val partsInCompletion = AtomicInteger()
        val checksumsInCompletion = AtomicInteger()
        val partChecksumAlgorithms = ConcurrentHashMap<Int, String>()
        @Volatile var checksumAlgorithm: String? = null
        @Volatile var checksumType: String? = null
        val completing = CountDownLatch(1)
        val allowCompletion = CountDownLatch(1)
        val aborted = CountDownLatch(1)
        @Volatile var contentType: String? = null
        @Volatile var batchId: String? = null

        init {
            server.executor = workers
            server.createContext("/") { exchange ->
                exchange.use {
                    try {
                        handle(it)
                    } catch (t: Throwable) {
                        reply(
                            it,
                            500,
                            "<Error><Code>InternalError</Code><Message>${t.javaClass.simpleName}</Message></Error>",
                        )
                    }
                }
            }
            server.start()
        }

        private fun handle(exchange: HttpExchange) {
            val query =
                exchange.requestURI.rawQuery.orEmpty().split('&').associate {
                    it.substringBefore('=') to it.substringAfter('=', "")
                }
            when {
                exchange.requestMethod == "POST" && "uploads" in query -> {
                    creates.incrementAndGet()
                    contentType = exchange.requestHeaders.getFirst("Content-Type")
                    checksumAlgorithm = exchange.requestHeaders.getFirst("x-amz-checksum-algorithm")
                    checksumType = exchange.requestHeaders.getFirst("x-amz-checksum-type")
                    batchId = exchange.requestHeaders.getFirst("x-amz-meta-batch-id")
                    reply(
                        exchange,
                        200,
                        "<InitiateMultipartUploadResult><Bucket>archive</Bucket><Key>fusion/batch.csv.gz</Key><UploadId>upload</UploadId></InitiateMultipartUploadResult>",
                    )
                }
                exchange.requestMethod == "PUT" && "partNumber" in query -> {
                    val part = query.getValue("partNumber").toInt()
                    exchange.requestHeaders.getFirst("x-amz-sdk-checksum-algorithm")?.let {
                        partChecksumAlgorithms[part] = it
                    }
                    twoPartsStarted.countDown()
                    thirdPartStarted.countDown()
                    check(allowParts.await(30, TimeUnit.SECONDS))
                    val attempt =
                        attempts.computeIfAbsent(part) { AtomicInteger() }.incrementAndGet()
                    if (part == 2 && attempt == 1 && failBeforeConsumption) {
                        exchange.requestBody.readNBytes(1024)
                        reply(
                            exchange,
                            503,
                            "<Error><Code>SlowDown</Code><Message>early injected failure</Message></Error>",
                        )
                        return
                    }
                    val hash = wireDigest(exchange)
                    digests
                        .computeIfAbsent(part) {
                            java.util.Collections.synchronizedList(mutableListOf())
                        }
                        .add(hash)
                    if (part == 2 && (failPermanently || (failOnce && attempt == 1))) {
                        val code = if (failPermanently) 400 else 503
                        val error = if (failPermanently) "InvalidRequest" else "SlowDown"
                        reply(
                            exchange,
                            code,
                            "<Error><Code>$error</Code><Message>injected failure</Message></Error>",
                        )
                    } else {
                        exchange.responseHeaders.add("ETag", "\"part-$part\"")
                        reply(exchange, 200, "")
                    }
                }
                exchange.requestMethod == "POST" && "uploadId" in query -> {
                    val xml = exchange.requestBody.readBytes().toString(Charsets.UTF_8)
                    partsInCompletion.set(Regex("<Part>").findAll(xml).count())
                    checksumsInCompletion.set(Regex("<ChecksumCRC32>").findAll(xml).count())
                    completing.countDown()
                    check(allowCompletion.await(30, TimeUnit.SECONDS))
                    reply(
                        exchange,
                        200,
                        "<CompleteMultipartUploadResult><Bucket>archive</Bucket><Key>fusion/batch.csv.gz</Key><ETag>\"done\"</ETag></CompleteMultipartUploadResult>",
                    )
                }
                exchange.requestMethod == "DELETE" && "uploadId" in query -> {
                    aborts.incrementAndGet()
                    reply(exchange, 204, "")
                    aborted.countDown()
                }
                else -> reply(exchange, 400, "<Error><Code>InvalidRequest</Code></Error>")
            }
        }

        private fun wireDigest(exchange: HttpExchange): ByteArray {
            val input = BufferedInputStream(exchange.requestBody)
            val hash = MessageDigest.getInstance("SHA-256")
            val crc = java.util.zip.CRC32()
            if (
                !exchange.requestHeaders
                    .getFirst("Content-Encoding")
                    .orEmpty()
                    .contains("aws-chunked")
            ) {
                updateDigest(input, Long.MAX_VALUE, hash, crc)
            } else {
                // Decode the SDK aws-chunked envelope after HttpServer removes HTTP chunking.
                while (true) {
                    val size = line(input).substringBefore(';').toLong(16)
                    if (size == 0L) break
                    updateDigest(input, size, hash, crc)
                    check(line(input).isEmpty())
                }
            }
            exchange.responseHeaders.add(
                "x-amz-checksum-crc32",
                java.util.Base64.getEncoder()
                    .encodeToString(
                        java.nio.ByteBuffer.allocate(4).putInt(crc.value.toInt()).array()
                    )
            )
            return hash.digest()
        }

        private fun line(input: InputStream): String {
            val result = StringBuilder()
            while (true) {
                val next = input.read()
                check(next >= 0)
                if (next == 10) return result.toString().removeSuffix("\r")
                result.append(next.toChar())
                check(result.length < 16384)
            }
        }

        private fun reply(exchange: HttpExchange, status: Int, xml: String) {
            val bytes = xml.toByteArray()
            exchange.responseHeaders.add("Content-Type", "application/xml")
            exchange.sendResponseHeaders(status, if (bytes.isEmpty()) -1 else bytes.size.toLong())
            if (bytes.isNotEmpty()) exchange.responseBody.write(bytes)
        }

        override fun close() {
            allowCompletion.countDown()
            allowParts.countDown()
            server.stop(0)
            workers.shutdownNow()
            check(workers.awaitTermination(5, TimeUnit.SECONDS))
        }
    }

    companion object {
        private fun digest(input: InputStream, size: Long): ByteArray {
            val hash = MessageDigest.getInstance("SHA-256")
            updateDigest(input, size, hash)
            return hash.digest()
        }

        private fun updateDigest(
            input: InputStream,
            size: Long,
            hash: MessageDigest,
            crc: java.util.zip.CRC32? = null
        ) {
            val buffer = ByteArray(8192)
            var remaining = size
            while (remaining > 0) {
                val read = input.read(buffer, 0, minOf(buffer.size.toLong(), remaining).toInt())
                if (read == -1) break
                hash.update(buffer, 0, read)
                crc?.update(buffer, 0, read)
                remaining -= read
            }
        }
    }
}
