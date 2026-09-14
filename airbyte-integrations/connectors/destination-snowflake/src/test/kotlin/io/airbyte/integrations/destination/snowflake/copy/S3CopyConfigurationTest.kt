package io.airbyte.integrations.destination.snowflake.copy

import io.airbyte.integrations.destination.snowflake.cdk.SnowflakeMigratingConfigurationSpecificationSupplier
import io.airbyte.integrations.destination.snowflake.spec.SnowflakeSpecification
import java.util.UUID
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertNull
import org.junit.jupiter.api.Assertions.assertThrows
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test

class S3CopyConfigurationTest {
    private val names = listOf("organization", "workspace", "source", "connection", "destination")
    private val environment =
        mapOf(
            "AIRBYTE_S3_COPY_ENABLED" to "true",
            "AIRBYTE_S3_COPY_BUCKET" to "test-bucket",
            "AIRBYTE_S3_COPY_REGION" to "test-region",
            "AIRBYTE_S3_COPY_ROLE_ARN" to "test-role",
        )

    private fun spec(ids: Map<String, String?>): SnowflakeSpecification {
        val json =
            ids.entries.joinToString(prefix = "{", postfix = "}") { (name, value) ->
                "\"${name}_id\":" + (value?.let { "\"$it\"" } ?: "null")
            }
        return SnowflakeMigratingConfigurationSpecificationSupplier(json).get()
    }

    private fun ids(config: S3CopyConfiguration) =
        listOf(
            config.organizationId,
            config.workspaceId,
            config.sourceId,
            config.connectionId,
            config.destinationId
        )

    @Test
    fun `all IDs default to zero and null config IDs use environment`() {
        assertEquals(
            List(5) { UUID(0, 0) },
            ids(S3CopyConfiguration.fromEnvironment(SnowflakeSpecification(), environment)!!)
        )
        val values = names.mapIndexed { i, name -> name to UUID(0, i + 1L).toString() }.toMap()
        val env = environment + values.mapKeys { "AIRBYTE_S3_COPY_${it.key.uppercase()}_ID" }
        assertEquals(
            values.values.map(UUID::fromString),
            ids(S3CopyConfiguration.fromEnvironment(spec(names.associateWith { null }), env)!!)
        )
    }

    @Test
    fun `config UUIDs override environment independently and normalize uppercase`() {
        val uuid = "AABBCCDD-ABCD-1234-ABCD-1234567890AB"
        names.forEachIndexed { index, name ->
            val env =
                environment +
                    names.associate {
                        "AIRBYTE_S3_COPY_${it.uppercase()}_ID" to UUID(0, 1).toString()
                    }
            val result = ids(S3CopyConfiguration.fromEnvironment(spec(mapOf(name to uuid)), env)!!)
            assertEquals(UUID.fromString(uuid), result[index])
            assertEquals(uuid.lowercase(), result[index].toString())
            result.filterIndexed { i, _ -> i != index }.forEach { assertEquals(UUID(0, 1), it) }
            // A valid config override wins even if the environment fallback is malformed.
            assertEquals(
                UUID.fromString(uuid),
                ids(
                    S3CopyConfiguration.fromEnvironment(
                        spec(mapOf(name to uuid)),
                        environment + ("AIRBYTE_S3_COPY_${name.uppercase()}_ID" to "bad")
                    )!!
                )[index]
            )
        }
    }

    @Test
    fun `reject malformed optional IDs in config and environment`() {
        names.forEach { name ->
            listOf(
                    "",
                    " ",
                    "bad",
                    "1-1-1-1-1",
                    "00000000000000000000000000000000",
                    "00000000-0000-0000-0000-000000000000 "
                )
                .forEach { bad ->
                    val error =
                        assertThrows(IllegalArgumentException::class.java) {
                            S3CopyConfiguration.fromEnvironment(
                                spec(mapOf(name to bad)),
                                environment
                            )
                        }
                    assertTrue(error.message!!.contains("${name}_id"))
                    assertThrows(IllegalArgumentException::class.java) {
                        S3CopyConfiguration.fromEnvironment(
                            SnowflakeSpecification(),
                            environment + ("AIRBYTE_S3_COPY_${name.uppercase()}_ID" to bad)
                        )
                    }
                }
        }
    }

    @Test
    fun `disabled helper ignores routing and optional IDs`() {
        assertNull(
            S3CopyConfiguration.fromEnvironment(spec(mapOf("organization" to "bad")), emptyMap())
        )
        assertNull(
            S3CopyConfiguration.fromEnvironment(
                SnowflakeSpecification(),
                mapOf("AIRBYTE_S3_COPY_ENABLED" to "false")
            )
        )
        assertThrows(IllegalArgumentException::class.java) {
            S3CopyConfiguration.fromEnvironment(
                SnowflakeSpecification(),
                mapOf("AIRBYTE_S3_COPY_ENABLED" to "yes")
            )
        }
    }

    @Test
    fun `preview forces route while preserving ID and external ID overrides`() {
        val env =
            environment +
                mapOf(
                    "AIRBYTE_S3_COPY_ENABLED" to "false",
                    "AIRBYTE_S3_COPY_PREFIX" to "other",
                    "AIRBYTE_S3_COPY_ORGANIZATION_ID" to UUID(0, 7).toString(),
                    "AIRBYTE_S3_COPY_EXTERNAL_ID" to "external"
                )
        val preview = S3CopyConfiguration.previewEnvironment(env)
        val config =
            S3CopyConfiguration.fromEnvironment(
                spec(mapOf("destination" to UUID(0, 8).toString())),
                preview
            )!!
        assertEquals("false", env["AIRBYTE_S3_COPY_ENABLED"])
        assertEquals("true", preview["AIRBYTE_S3_COPY_ENABLED"])
        assertEquals("airbyte-fusion-context-store", config.bucket)
        assertEquals("us-west-2", config.region)
        assertEquals("arn:aws:iam::506572016262:role/fusion-snowflake-sync-copy", config.roleArn)
        assertEquals("fusion", config.prefix)
        assertEquals(UUID(0, 7), config.organizationId)
        assertEquals(UUID(0, 8), config.destinationId)
        assertEquals("external", config.externalId)
        assertEquals(
            "test-bucket",
            S3CopyConfiguration.fromEnvironment(SnowflakeSpecification(), environment)!!.bucket
        )
    }
}
