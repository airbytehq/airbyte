/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.util

import java.io.InputStream

fun InputStream.lineSequence(): Sequence<String> = bufferedReader(Charsets.UTF_8).lineSequence()
