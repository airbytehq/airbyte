/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.standardtest.source

import com.fasterxml.jackson.databind.JsonNode
import com.google.common.collect.Lists
import com.google.common.collect.Streams
import io.airbyte.commons.io.IOs
import io.airbyte.commons.io.LineGobbler
import io.airbyte.commons.json.Jsons
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import io.airbyte.protocol.models.v0.ConnectorSpecification
import io.airbyte.workers.TestHarnessUtils
import io.github.oshai.kotlinlogging.KotlinLogging
import java.io.IOException
import java.nio.file.Files
import java.nio.file.Path
import java.util.*
import java.util.concurrent.TimeUnit
import java.util.function.Consumer
import org.junit.jupiter.api.Assertions

private val LOGGER = KotlinLogging.logger {}

/**
 * Extends TestSource such that it can be called using resources pulled from the file system. Will
 * also add the ability to execute arbitrary scripts in the next version.
 */
class PythonSourceAcceptanceTest : SourceAcceptanceTest() {
    private lateinit var testRoot: Path

    @get:Throws(IOException::class)
    override val spec: ConnectorSpecification
        get() = runExecutable(Command.GET_SPEC, ConnectorSpecification::class.java)

    @get:Throws(IOException::class)
    override val config: JsonNode
        get() = runExecutable(Command.GET_CONFIG)

    @get:Throws(IOException::class)
    override val configuredCatalog: ConfiguredAirbyteCatalog
        get() = runExecutable(Command.GET_CONFIGURED_CATALOG, ConfiguredAirbyteCatalog::class.java)

    @get:Throws(IOException::class)
    override val state: JsonNode
        get() = runExecutable(Command.GET_STATE)

    @Throws(IOException::class)
    override fun assertFullRefreshMessages(allMessages: List<AirbyteMessage>) {
        val regexTests =
            Streams.stream(
                    runExecutable(Command.GET_REGEX_TESTS).withArray<JsonNode>("tests").elements()
                )
                .toList()
                .map { obj: JsonNode -> obj.textValue() }

        val stringMessages =
            allMessages.map { `object`: AirbyteMessage -> Jsons.serialize(`object`) }
        LOGGER.info("Running " + regexTests.size + " regex tests...")
        regexTests.forEach(
            Consumer { regex: String ->
                LOGGER.info("Looking for [$regex]")
                Assertions.assertTrue(
                    stringMessages.any { line: String -> line.matches(regex.toRegex()) },
                    "Failed to find regex: $regex"
                )
            }
        )
    }

    override val imageName: String
        get() = IMAGE_NAME

    @Throws(Exception::class)
    override fun setupEnvironment(environment: TestDestinationEnv?) {
        testRoot =
            Files.createTempDirectory(
                Files.createDirectories(Path.of("/tmp/standard_test")),
                "pytest"
            )
        runExecutableVoid(Command.SETUP)
    }

    @Throws(Exception::class)
    override fun tearDown(testEnv: TestDestinationEnv?) {
        runExecutableVoid(Command.TEARDOWN)
    }

    private enum class Command {
        GET_SPEC,
        GET_CONFIG,
        GET_CONFIGURED_CATALOG,
        GET_STATE,
        GET_REGEX_TESTS,
        SETUP,
        TEARDOWN
    }

    @Throws(IOException::class)
    private fun <T> runExecutable(cmd: Command, klass: Class<T>): T {
        return Jsons.`object`(runExecutable(cmd), klass)!!
    }

    @Throws(IOException::class)
    private fun runExecutable(cmd: Command): JsonNode {
        return Jsons.deserialize(IOs.readFile(runExecutableInternal(cmd), OUTPUT_FILENAME))
    }

    @Throws(IOException::class)
    private fun runExecutableVoid(cmd: Command) {
        runExecutableInternal(cmd)
    }

    @Throws(IOException::class)
    private fun runExecutableInternal(cmd: Command): Path {
        LOGGER.info("testRoot = $testRoot")
        val dockerCmd: List<String> =
            Lists.newArrayList(
                "docker",
                "run",
                "--rm",
                "-i",
                "-v",
                String.format("%s:%s", testRoot, "/test_root"),
                "-w",
                testRoot.toString(),
                "--network",
                "host",
                PYTHON_CONTAINER_NAME,
                cmd.toString().lowercase(Locale.getDefault()),
                "--out",
                "/test_root"
            )

        val process = ProcessBuilder(dockerCmd).start()
        LineGobbler.gobble(process.errorStream, { msg: String -> LOGGER.error(msg) })
        LineGobbler.gobble(process.inputStream, { msg: String -> LOGGER.info(msg) })

        TestHarnessUtils.gentleClose(process, 1, TimeUnit.MINUTES)

        val exitCode = process.exitValue()
        if (exitCode != 0) {
            throw RuntimeException("python execution failed")
        }

        return testRoot
    }

    companion object {

        private const val OUTPUT_FILENAME = "output.json"

        var IMAGE_NAME: String = "dummy_image_name"
        var PYTHON_CONTAINER_NAME: String? = null
    }
}
