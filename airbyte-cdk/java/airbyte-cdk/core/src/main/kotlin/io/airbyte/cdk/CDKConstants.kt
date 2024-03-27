/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk

import java.io.IOException
import java.util.*

object CDKConstants {
    val VERSION: String = version

    private val version: String
        get() {
            val prop = Properties()

            try {
                CDKConstants::class
                    .java
                    .classLoader
                    .getResourceAsStream("version.properties")
                    .use { inputStream ->
                        prop.load(inputStream)
                        return prop.getProperty("version")
                    }
            } catch (e: IOException) {
                throw RuntimeException("Could not read version properties file", e)
            }
        }
}
