/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.cdk.check

import io.airbyte.cdk.Operation
import io.airbyte.cdk.fakesource.FakeSourceCheckSectionHandler
import io.airbyte.cdk.fakesource.FakeSourceConfigurationSpecification
import io.airbyte.cdk.output.BufferingOutputConsumer
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus
import io.micronaut.context.annotation.Property
import io.micronaut.test.extensions.junit5.annotation.MicronautTest
import jakarta.inject.Inject
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

@MicronautTest(environments = ["source"], rebuildContext = true)
@Property(name = Operation.PROPERTY, value = "check")
class CheckTest {
    @Inject lateinit var checkOperation: CheckOperation<FakeSourceConfigurationSpecification>

    @Inject lateinit var outputConsumer: BufferingOutputConsumer

    @Inject lateinit var sectionHandler: FakeSourceCheckSectionHandler

    @Test
    @Property(name = "airbyte.connector.config.host", value = "localhost")
    @Property(name = "airbyte.connector.config.port", value = "-1")
    @Property(name = "airbyte.connector.config.database", value = "testdb")
    @Property(name = "metadata.resource", value = "discover/metadata-valid.json")
    fun testConfigBadPort() {
        // we don't validate the config against the jsonschema, so even though -1
        // isn't within the declared bounds (0<=it<=65536),
        // we should still succeed.
        // (the connector is responsible for catching this sort of thing)
        assertSucceeded()
    }

    @Test
    @Property(name = "airbyte.connector.config.host", value = "localhost")
    @Property(name = "airbyte.connector.config.database", value = "testdb")
    @Property(name = "metadata.resource", value = "discover/metadata-valid.json")
    fun testSuccess() {
        assertSucceeded()
    }

    @Test
    @Property(name = "airbyte.connector.config.host", value = "localhost")
    @Property(name = "airbyte.connector.config.database", value = "testdb")
    @Property(name = "metadata.resource", value = "discover/metadata-empty.json")
    fun testBadSchema() {
        assertFailed("Discovered zero tables".toRegex())
    }

    @Test
    @Property(name = "airbyte.connector.config.host", value = "localhost")
    @Property(name = "airbyte.connector.config.database", value = "testdb")
    @Property(name = "metadata.resource", value = "discover/metadata-column-query-fails.json")
    fun testBadTables() {
        assertFailed("Unable to query any of the [0-9]+ discovered table".toRegex())
    }

    @Test
    @Property(
        name = "airbyte.connector.config.json",
        value = """{"host":"localhost","check-section":"connection"}""",
    )
    @Property(name = "metadata.resource", value = "discover/metadata-valid.json")
    fun testSectionCheckGoesToTheHandler() {
        // The partial config lacks the required `database`: only the handler runs, not the factory.
        assertSucceeded()
        Assertions.assertEquals(listOf("connection"), sectionHandler.checkedSections)
    }

    @Test
    @Property(
        name = "airbyte.connector.config.json",
        value = """{"host":"unreachable","check-section":"connection"}""",
    )
    @Property(name = "metadata.resource", value = "discover/metadata-valid.json")
    fun testSectionCheckFailureComesFromTheHandler() {
        assertFailed("Host 'unreachable' cannot be reached".toRegex())
        Assertions.assertEquals(listOf("connection"), sectionHandler.checkedSections)
    }

    @Test
    @Property(
        name = "airbyte.connector.config.json",
        value = """{"host":"localhost","database":"testdb","check-section":"sync_method"}""",
    )
    @Property(name = "metadata.resource", value = "discover/metadata-empty.json")
    fun testLastSectionRunsTheFullCheck() {
        // "Discovered zero tables" can only come from the full check.
        assertFailed("Discovered zero tables".toRegex())
        Assertions.assertEquals(emptyList<String>(), sectionHandler.checkedSections)
    }

    @Test
    @Property(
        name = "airbyte.connector.config.json",
        value = """{"host":"localhost","check-section":"nope"}""",
    )
    @Property(name = "metadata.resource", value = "discover/metadata-valid.json")
    fun testUnknownSection() {
        assertFailed("Unknown check-section 'nope'; .* connection, naming, sync_method".toRegex())
        Assertions.assertEquals(emptyList<String>(), sectionHandler.checkedSections)
    }

    @Test
    @Property(
        name = "airbyte.connector.config.json",
        value = """{"host":"localhost","check-section":"naming"}""",
    )
    @Property(name = "metadata.resource", value = "discover/metadata-valid.json")
    fun testSectionWithoutCheckIsRejected() {
        // `naming` is declared with `"check": false`: neither the handler nor the full check runs.
        assertFailed(
            "Section 'naming' cannot be checked on its own; .* connection, sync_method".toRegex(),
        )
        Assertions.assertEquals(emptyList<String>(), sectionHandler.checkedSections)
    }

    @Test
    @Property(
        name = "airbyte.connector.config.json",
        value = """{"host":"localhost","check-section":5}""",
    )
    @Property(name = "metadata.resource", value = "discover/metadata-valid.json")
    fun testSectionMustBeAString() {
        assertFailed("'check-section' must be a string".toRegex())
    }

    @Test
    @Property(name = "airbyte.connector.config.host", value = "localhost")
    @Property(name = "airbyte.connector.config.database", value = "testdb")
    @Property(name = "airbyte.connector.config.check-section", value = "connection")
    @Property(name = "metadata.resource", value = "discover/metadata-valid.json")
    fun testSectionFromMicronautProperty() {
        assertSucceeded()
        Assertions.assertEquals(listOf("connection"), sectionHandler.checkedSections)
    }

    fun assertSucceeded() {
        assert(null)
    }

    fun assertFailed(regex: Regex) {
        assert(regex)
    }

    fun assert(failureRegex: Regex?) {
        checkOperation.execute()
        val statuses: List<AirbyteConnectionStatus> = outputConsumer.statuses()
        Assertions.assertEquals(1, statuses.size, statuses.toString())
        val actual: AirbyteConnectionStatus = statuses.first()
        if (failureRegex == null) {
            Assertions.assertEquals(
                AirbyteConnectionStatus.Status.SUCCEEDED,
                actual.status,
                actual.toString(),
            )
        } else {
            Assertions.assertEquals(
                AirbyteConnectionStatus.Status.FAILED,
                actual.status,
                actual.toString(),
            )
            Assertions.assertTrue(failureRegex.containsMatchIn(actual.message), actual.message)
        }
    }
}
