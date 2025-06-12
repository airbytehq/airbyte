/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.file

import java.io.BufferedOutputStream
import java.io.ByteArrayOutputStream
import java.io.OutputStream
import java.util.zip.GZIPOutputStream

interface StreamProcessor<T : OutputStream> {
    val wrapper: (ByteArrayOutputStream) -> T
    val partFinisher: T.() -> Unit
    val extension: String?
}

data object NoopProcessor : StreamProcessor<ByteArrayOutputStream> {
    override val wrapper: (ByteArrayOutputStream) -> ByteArrayOutputStream = { it }
    override val partFinisher: ByteArrayOutputStream.() -> Unit = {}
    override val extension: String? = null
}

data object GZIPProcessor : StreamProcessor<BufferedOutputStream> {
    override val wrapper: (ByteArrayOutputStream) -> BufferedOutputStream = {
        BufferedOutputStream(GZIPOutputStream(it))
    }
    override val partFinisher: BufferedOutputStream.() -> Unit = { close() }
    override val extension: String = "gz"
}
