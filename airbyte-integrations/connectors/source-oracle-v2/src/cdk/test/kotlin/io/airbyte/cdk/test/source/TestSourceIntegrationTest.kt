/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.test.source

import com.deblock.jsondiff.DiffGenerator
import com.deblock.jsondiff.diff.JsonDiff
import com.deblock.jsondiff.matcher.CompositeJsonMatcher
import com.deblock.jsondiff.matcher.JsonMatcher
import com.deblock.jsondiff.matcher.LenientJsonObjectPartialMatcher
import com.deblock.jsondiff.matcher.StrictJsonArrayPartialMatcher
import com.deblock.jsondiff.matcher.StrictPrimitivePartialMatcher
import com.deblock.jsondiff.viewer.OnlyErrorDiffViewer
import io.airbyte.cdk.command.CliRunner
import io.airbyte.cdk.consumers.BufferingOutputConsumer
import io.airbyte.cdk.jdbc.H2TestFixture
import io.airbyte.cdk.operation.OperationType
import io.airbyte.cdk.ssh.SshBastionContainer
import io.airbyte.cdk.testcontainers.DOCKER_HOST_FROM_WITHIN_CONTAINER
import io.airbyte.commons.json.Jsons
import io.airbyte.commons.resources.MoreResources
import io.airbyte.protocol.models.v0.AirbyteCatalog
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus
import io.airbyte.protocol.models.v0.ConnectorSpecification
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test
import org.testcontainers.Testcontainers

class TestSourceIntegrationTest {

    @Test
    fun testSpec() {
        val output: BufferingOutputConsumer = CliRunner.runSource(OperationType.SPEC)
        val actual: String = Jsons.serialize(output.specs().last())

        val jsonMatcher: JsonMatcher =
            CompositeJsonMatcher(
                StrictJsonArrayPartialMatcher(),
                LenientJsonObjectPartialMatcher(),
                StrictPrimitivePartialMatcher(),
            )
        val diff: JsonDiff = DiffGenerator.diff(Jsons.serialize(expectedSpec), actual, jsonMatcher)
        Assertions.assertEquals("", OnlyErrorDiffViewer.from(diff).toString())
    }

    val expectedSpec: ConnectorSpecification =
        Jsons.deserialize(
            MoreResources.readResource("test/source/expected-spec.json"),
            ConnectorSpecification::class.java
        )

    val h2 = H2TestFixture()
    init {
        Testcontainers.exposeHostPorts(h2.port)
        h2.execute(
            """CREATE TABLE kv (
            |k INT PRIMARY KEY, 
            |v VARCHAR(60))
            |"""
                .trimMargin()
                .replace('\n', ' ')
        )
        h2.execute(
            """CREATE TABLE events (
            |id UUID GENERATED ALWAYS AS (RANDOM_UUID()) PRIMARY KEY,
            |ts TIMESTAMP WITH TIME ZONE NOT NULL, 
            |msg VARCHAR(60))
            |"""
                .trimMargin()
                .replace('\n', ' ')
        )
    }
    val sshBastion = SshBastionContainer(tunnelingToHostPort = h2.port)

    @Test
    fun testCheckAndDiscoverNoTunnel() {
        testCheckAndDiscover(
            TestSourceConfigurationJsonObject().apply {
                port = h2.port
                database = h2.database
            }
        )
    }

    @Test
    fun testCheckAndDiscoverSshKeyAuth() {
        testCheckAndDiscover(
            TestSourceConfigurationJsonObject().apply {
                host = DOCKER_HOST_FROM_WITHIN_CONTAINER // required only because of container
                port = h2.port
                database = h2.database
                setTunnelMethodValue(sshBastion.outerKeyAuthTunnelMethod)
            }
        )
    }

    @Test
    fun testCheckAndDiscoverSshPasswordAuth() {
        testCheckAndDiscover(
            TestSourceConfigurationJsonObject().apply {
                host = DOCKER_HOST_FROM_WITHIN_CONTAINER // required only because of container
                port = h2.port
                database = h2.database
                setTunnelMethodValue(sshBastion.outerPasswordAuthTunnelMethod)
            }
        )
    }

    private fun testCheckAndDiscover(configPojo: TestSourceConfigurationJsonObject) {
        val checkOutput: BufferingOutputConsumer =
            CliRunner.runSource(OperationType.CHECK, configPojo)
        Assertions.assertEquals(
            listOf(AirbyteConnectionStatus().withStatus(AirbyteConnectionStatus.Status.SUCCEEDED)),
            checkOutput.statuses()
        )
        val discoverOutput: BufferingOutputConsumer =
            CliRunner.runSource(OperationType.DISCOVER, configPojo)
        Assertions.assertEquals(listOf(expectedCatalog), discoverOutput.catalogs())
    }

    val expectedCatalog: AirbyteCatalog =
        Jsons.deserialize(
            MoreResources.readResource("test/source/expected-catalog.json"),
            AirbyteCatalog::class.java
        )
}
