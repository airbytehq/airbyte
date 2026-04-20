/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.file.object_storage

class PathMatcherException(
    override val message: String,
    override val cause: Throwable,
) : Throwable(message, cause)
