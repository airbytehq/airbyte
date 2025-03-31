/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.util

import java.io.OutputStream

fun OutputStream.write(string: String) {
    write(string.toByteArray(Charsets.UTF_8))
}
