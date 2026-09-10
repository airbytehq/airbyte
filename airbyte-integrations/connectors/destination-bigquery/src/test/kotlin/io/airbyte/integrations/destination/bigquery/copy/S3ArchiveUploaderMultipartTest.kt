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
import kotlinx.coroutines.runBlocking
import kotlinx.coroutines.withContext
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
    ) : AutoCloseable {
        private val workers = Executors.newFixedThreadPool(4)
        private val server = HttpServer.create(InetSocketAddress("127.0.0.1", 0), 0)
        val port: Int
            get() = server.address.port

        val digests = ConcurrentHashMap<Int, MutableList<ByteArray>>()
        val attempts = ConcurrentHashMap<Int, AtomicInteger>()
        val creates = AtomicInteger()
        val aborts = AtomicInteger()
        val partsInCompletion = AtomicInteger()
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
                    batchId = exchange.requestHeaders.getFirst("x-amz-meta-batch-id")
                    reply(
                        exchange,
                        200,
                        "<InitiateMultipartUploadResult><Bucket>archive</Bucket><Key>fusion/batch.csv.gz</Key><UploadId>upload</UploadId></InitiateMultipartUploadResult>",
                    )
                }
                exchange.requestMethod == "PUT" && "partNumber" in query -> {
                    val part = query.getValue("partNumber").toInt()
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
                    if (part == 2 && (failPermanently || attempt == 1)) {
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
            if (
                !exchange.requestHeaders
                    .getFirst("Content-Encoding")
                    .orEmpty()
                    .contains("aws-chunked")
            ) {
                return digest(input, Long.MAX_VALUE)
            }
            // HTTP chunking is decoded by HttpServer; decode the SDK's separate aws-chunked
            // envelope.
            val hash = MessageDigest.getInstance("SHA-256")
            while (true) {
                val size = line(input).substringBefore(';').toLong(16)
                if (size == 0L) break
                updateDigest(input, size, hash)
                check(line(input).isEmpty())
            }
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

        private fun updateDigest(input: InputStream, size: Long, hash: MessageDigest) {
            val buffer = ByteArray(8192)
            var remaining = size
            while (remaining > 0) {
                val read = input.read(buffer, 0, minOf(buffer.size.toLong(), remaining).toInt())
                if (read == -1) break
                hash.update(buffer, 0, read)
                remaining -= read
            }
        }
    }
}
