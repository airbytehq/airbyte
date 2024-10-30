/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.file

import java.io.ByteArrayOutputStream
import java.util.zip.GZIPOutputStream

interface StreamProcessor<T> {
    val wrapper: (ByteArrayOutputStream) -> T
    val partFinisher: T.() -> Unit
    val extension: String?
}

data object NoopProcessor : StreamProcessor<ByteArrayOutputStream> {
    override val wrapper: (ByteArrayOutputStream) -> ByteArrayOutputStream = { it }
    override val partFinisher: ByteArrayOutputStream.() -> Unit = {}
    override val extension: String? = null
}

data object GZIPProcessor : StreamProcessor<GZIPOutputStream> {
    override val wrapper: (ByteArrayOutputStream) -> GZIPOutputStream = { GZIPOutputStream(it) }
    override val partFinisher: GZIPOutputStream.() -> Unit = { finish() }
    override val extension: String = "gz"
}
