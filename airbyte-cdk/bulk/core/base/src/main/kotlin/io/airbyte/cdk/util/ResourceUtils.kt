/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.cdk.util

import java.net.URL

object ResourceUtils {
    @JvmStatic
    fun readResource(resourceName: String): String =
        getResource(resourceName).openStream().reader().readText()

    @JvmStatic
    fun getResource(resourceName: String): URL {
        val loader: ClassLoader =
            listOfNotNull(
                    Thread.currentThread().contextClassLoader,
                    ResourceUtils::class.java.classLoader,
                )
                .firstOrNull()
                ?: throw RuntimeException("no ClassLoader found")
        return loader.getResource(resourceName) ?: throw RuntimeException("resource not found")
    }
}
