/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.http

import java.io.Closeable
import java.io.InputStream

interface Response : Closeable {
    val statusCode: Int
    val headers: Map<String, List<String>>
    val body: InputStream?
}

fun Response.consumeBodyToString(): String =
    this.use { body?.reader(Charsets.UTF_8)?.readText() ?: "" }

fun Response.getBodyOrEmpty(): InputStream = this.body ?: InputStream.nullInputStream()
