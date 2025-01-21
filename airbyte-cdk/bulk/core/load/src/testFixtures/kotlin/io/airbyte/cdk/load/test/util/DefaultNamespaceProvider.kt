/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.test.util

interface DefaultNamespaceProvider {
    fun get(randomNamespace: String): String?
}

class DefaultDefaultNamespaceProvider : DefaultNamespaceProvider {
    override fun get(randomNamespace: String): String? = null
}
