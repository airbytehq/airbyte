/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.configoss

import java.io.File

/** This interface represents configuration objects used by Airbyte and Airbyte cloud */
interface AirbyteConfig {
    fun getName(): String?

    /** @return the name of the field storing the id for the configuration object */
    val idFieldName: String?

    /** @return the actual id of the configuration object */
    fun <T> getId(config: T): String

    /** @return the path to the yaml file that defines the schema of the configuration object */
    val configSchemaFile: File

    fun <T> getClassName(): Class<T>
}
