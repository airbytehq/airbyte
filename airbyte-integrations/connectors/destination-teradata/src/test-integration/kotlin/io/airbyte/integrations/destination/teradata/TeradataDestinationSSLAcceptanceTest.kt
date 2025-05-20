/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.teradata

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.commons.json.Jsons
import java.nio.file.Files
import java.nio.file.Paths
import org.junit.jupiter.api.TestInstance
import org.slf4j.Logger
import org.slf4j.LoggerFactory

@TestInstance(TestInstance.Lifecycle.PER_CLASS)
class TeradataDestinationSSLAcceptanceTest : TeradataDestinationAcceptanceTest() {
    @get:Throws(Exception::class)
    override val staticConfig: JsonNode
        get() = Jsons.deserialize(Files.readString(Paths.get("secrets/sslconfig.json")))

    companion object {
        private val LOGGER: Logger =
            LoggerFactory.getLogger(
                TeradataDestinationSSLAcceptanceTest::class.java,
            )
    }
}
