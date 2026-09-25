/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.slackv2

import io.airbyte.cdk.command.SyncsTestFixture
import io.airbyte.integrations.source.slackv2.SlackTestSupport.config
import io.airbyte.integrations.source.slackv2.SlackTestSupport.withServer
import org.junit.jupiter.api.AfterAll
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.BeforeAll
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.parallel.Isolated

/** Runs CHECK against the fake Slack server. */
/** Runs alone: the fake server, its request log and the system properties are shared state. */
@Isolated
class SlackSourceCheckTest {

    @Test
    fun testCheckSucceedsWithBotToken() {
        withServer(server) { SyncsTestFixture.testCheck(config(server)) }
        Assertions.assertTrue(server.requests.any { it.method == "auth.test" && it.status == 200 })
        Assertions.assertTrue(
            server.requests.any { it.method == "users.list" && it.params["limit"] == "1" }
        )
    }

    @Test
    fun testCheckSucceedsWithOAuthToken() {
        withServer(server) {
            SyncsTestFixture.testCheck(
                config(server, token = FakeSlackData.OAUTH_TOKEN, oauth = true)
            )
        }
    }

    @Test
    fun testCheckFailsWithInvalidToken() {
        withServer(server) {
            SyncsTestFixture.testCheck(
                config(server, token = "xoxb-wrong"),
                expectedFailure = "Slack API authentication/permission error: invalid_auth",
            )
        }
    }

    @Test
    fun testCheckFailsWithBlankToken() {
        withServer(server) {
            SyncsTestFixture.testCheck(
                config(server, token = " "),
                expectedFailure = "'credentials.api_token' property must not be blank"
            )
        }
    }

    @Test
    fun testCheckFailsWhenUnreachable() {
        withServer(
            server,
            mapOf(
                SlackSourceConfigurationFactory.API_BASE_URL_PROPERTY to "http://localhost:1/api/"
            )
        ) {
            SyncsTestFixture.testCheck(
                config(server),
                expectedFailure = "Could not reach the Slack API"
            )
        }
    }

    /** A transient error on the way is retried, not surfaced. */
    @Test
    fun testCheckRetriesTransientErrors() {
        server.injectError("auth.test", FakeSlackServer.InjectedError(200, "internal_error"))
        server.injectError("auth.test", FakeSlackServer.InjectedError(503, null))
        server.injectError(
            "users.list",
            FakeSlackServer.InjectedError(429, "ratelimited", retryAfter = 1)
        )
        withServer(server) { SyncsTestFixture.testCheck(config(server)) }
    }

    companion object {
        lateinit var server: FakeSlackServer

        @JvmStatic
        @BeforeAll
        fun startServer() {
            server = FakeSlackServer(FakeSlackData.generate(messagesPerChannel = 5)).start()
        }

        @JvmStatic
        @AfterAll
        fun stopServer() {
            server.stop()
        }
    }
}
