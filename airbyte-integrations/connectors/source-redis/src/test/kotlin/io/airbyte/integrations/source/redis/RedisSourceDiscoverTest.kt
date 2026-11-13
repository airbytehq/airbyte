/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.redis

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.command.CliRunner
import io.airbyte.cdk.util.Jsons
import io.airbyte.cdk.util.ResourceUtils
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test
import org.testcontainers.containers.GenericContainer

class RedisSourceDiscoverTest {
    @Test
    fun testDiscoverMatchesCatalogWithSeededKeysAndSecondDatabase() {
        redisContainer().use { redis ->
            redis.start()
            seed(redis)
            val result =
                redis.execInContainer("redis-cli", "-n", "1", "SET", "another:string", "db-one")
            Assertions.assertEquals(0, result.exitCode, result.stderr)
            assertCatalog(redis)
        }
    }

    @Test
    fun testDiscoverMatchesCatalogForEmptyRedis() {
        redisContainer().use { redis ->
            redis.start()
            assertCatalog(redis)
        }
    }

    private fun assertCatalog(redis: GenericContainer<*>) {
        val actual =
            CliRunner.source(
                    "discover",
                    RedisSourceConfigurationSpecification().apply {
                        host = redis.host
                        port = redis.getMappedPort(REDIS_PORT)
                    },
                )
                .run()
                .catalogs()
                .single()
        val expected = Jsons.readTree(ResourceUtils.readResource(EXPECTED_CATALOG))
        val actualJson: JsonNode = Jsons.valueToTree(actual)
        for (stream in actualJson["streams"]) {
            if (stream["source_defined_cursor"]?.asBoolean() != true) {
                (stream as ObjectNode).remove("default_cursor_field")
            }
        }
        Assertions.assertEquals(expected, actualJson)
    }

    private fun seed(redis: GenericContainer<*>) {
        for (args in
            listOf(
                listOf("SET", "a:string", "text"),
                listOf("HSET", "a:hash", "field", "value"),
                listOf("LPUSH", "a:list", "one", "two"),
                listOf("SADD", "a:set", "one", "two"),
                listOf("ZADD", "a:sorted-set", "1", "one"),
                listOf("XADD", "a:stream", "*", "field", "value"),
            )) {
            val result = redis.execInContainer(*(listOf("redis-cli") + args).toTypedArray())
            Assertions.assertEquals(0, result.exitCode, result.stderr)
        }
    }

    private fun redisContainer(): GenericContainer<*> =
        RedisTestContainer().withExposedPorts(REDIS_PORT)

    companion object {
        private const val REDIS_IMAGE = "redis:8"
        private const val REDIS_PORT = 6379
        private const val EXPECTED_CATALOG = "expected-catalog.json"
    }
}
