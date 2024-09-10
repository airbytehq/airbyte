/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.standardtest.source.fs

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.integrations.standardtest.source.SourceAcceptanceTest
import io.airbyte.cdk.integrations.standardtest.source.TestDestinationEnv
import io.airbyte.commons.io.IOs
import io.airbyte.commons.json.Jsons
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import io.airbyte.protocol.models.v0.ConnectorSpecification
import java.nio.file.Path

/**
 * Extends TestSource such that it can be called using resources pulled from the file system. Will
 * also add the ability to execute arbitrary scripts in the next version.
 */
class ExecutableTestSource : SourceAcceptanceTest() {
    class TestConfig(
        val imageName: String,
        val specPath: Path,
        val configPath: Path,
        val catalogPath: Path,
        val statePath: Path?
    )

    override val spec: ConnectorSpecification
        get() =
            Jsons.deserialize(
                IOs.readFile(TEST_CONFIG!!.specPath),
                ConnectorSpecification::class.java
            )

    override val imageName: String
        get() = TEST_CONFIG!!.imageName

    override val config: JsonNode
        get() = Jsons.deserialize(IOs.readFile(TEST_CONFIG!!.configPath))

    override val configuredCatalog: ConfiguredAirbyteCatalog
        get() =
            Jsons.deserialize(
                IOs.readFile(TEST_CONFIG!!.catalogPath),
                ConfiguredAirbyteCatalog::class.java
            )

    override val state: JsonNode
        get() =
            if (TEST_CONFIG!!.statePath != null) {
                Jsons.deserialize(IOs.readFile(TEST_CONFIG!!.statePath))
            } else {
                Jsons.deserialize("{}")
            }

    @Throws(Exception::class)
    override fun setupEnvironment(environment: TestDestinationEnv?) {
        // no-op, for now
    }

    @Throws(Exception::class)
    override fun tearDown(testEnv: TestDestinationEnv?) {
        // no-op, for now
    }

    companion object {
        var TEST_CONFIG: TestConfig? = null
    }
}
