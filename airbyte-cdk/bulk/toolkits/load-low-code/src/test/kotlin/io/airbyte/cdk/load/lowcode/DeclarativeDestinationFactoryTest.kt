/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.lowcode

import io.airbyte.cdk.load.check.dlq.DlqChecker
import io.airbyte.cdk.load.command.Append
import io.airbyte.cdk.load.command.Dedupe
import io.airbyte.cdk.load.command.DestinationConfiguration
import io.airbyte.cdk.load.command.DestinationOperation
import io.airbyte.cdk.load.command.Overwrite
import io.airbyte.cdk.load.command.SoftDelete
import io.airbyte.cdk.load.command.Update
import io.airbyte.cdk.load.command.dlq.DisabledObjectStorageConfig
import io.airbyte.cdk.load.command.dlq.ObjectStorageConfig
import io.airbyte.cdk.load.command.dlq.ObjectStorageConfigProvider
import io.airbyte.cdk.load.data.FieldType
import io.airbyte.cdk.load.data.ObjectType
import io.airbyte.cdk.load.data.StringType
import io.airbyte.cdk.load.http.authentication.BasicAccessAuthenticator
import io.airbyte.cdk.util.ResourceUtils
import io.mockk.EqMatcher
import io.mockk.every
import io.mockk.mockk
import io.mockk.mockkConstructor
import io.mockk.mockkStatic
import io.mockk.unmockkStatic
import io.mockk.verify
import kotlin.test.assertEquals
import org.junit.jupiter.api.Test

class MockConfig(
    val apiId: String,
    val apiToken: String,
    override val objectStorageConfig: ObjectStorageConfig = DisabledObjectStorageConfig(),
) : DestinationConfiguration(), ObjectStorageConfigProvider

val VALID_API_ID: String = "api_id"
val VALID_API_TOKEN: String = "api_token"

class DeclarativeDestinationFactoryTest {

    @Test
    internal fun `test when check then ensure check gets interpolated credentials`() {
        mockManifest(
            """
            checker:
              type: HttpRequestChecker
              requester:
                type: HttpRequester
                url: https://airbyte.io/
                method: GET
                authenticator:
                  type: BasicAccessAuthenticator
                  username: "{{ config.apiId }}"
                  password: "{{ config.apiToken }}"
            discovery:
              type: CompositeOperationsProvider
              operations:
                - type: StaticOperation
                  object_name: player
                  sync_mode:
                    type: Dedupe
                    primary_key: [[name]]
                    cursor: [updated_at]
                  schema:
                    type: object
                    required:
                      - name
                    additionalProperties: true
                    properties:
                      name:
                        type: string
                      updated_at:
                        type: string
                  matching_keys:
                    - [test]
        """.trimIndent()
        )

        val expectedOperations =
            listOf<DestinationOperation>(
                DestinationOperation(
                    "player",
                    Dedupe(listOf(listOf("name")), listOf("updated_at")),
                    ObjectType(
                        properties =
                            linkedMapOf(
                                "name" to FieldType(StringType, true),
                                "updated_at" to FieldType(StringType, true),
                            ),
                        additionalProperties = true,
                        required = listOf<String>("name"),
                    ),
                    matchingKeys = listOf<List<String>>(listOf<String>("test"))
                )
            )

        mockkConstructor(BasicAccessAuthenticator::class)
        val config = MockConfig(VALID_API_ID, VALID_API_TOKEN)
        val dlqChecker = mockk<DlqChecker>()
        every { dlqChecker.check(any()) } returns Unit

        try {
            DeclarativeDestinationFactory(config).createDestinationChecker(dlqChecker).check(config)

            verify {
                constructedWith<BasicAccessAuthenticator>(
                        EqMatcher(VALID_API_ID),
                        EqMatcher(VALID_API_TOKEN)
                    )
                    .intercept(any())
            }

            val actualOperations =
                DeclarativeDestinationFactory(config).createCompositeOperationsProvider().get()
            assertEquals(expectedOperations, actualOperations)
        } finally {
            unmockkStatic("io.airbyte.cdk.util.ResourceUtils") // Clean up mocks
        }
    }

    @Test
    internal fun `test static operations with all sync modes`() {
        mockManifest(
            """
            checker:
              type: HttpRequestChecker
              requester:
                type: HttpRequester
                url: https://airbyte.io/
                method: GET
                authenticator:
                  type: BasicAccessAuthenticator
                  username: "{{ config.apiId }}"
                  password: "{{ config.apiToken }}"
            discovery:
              type: CompositeOperationsProvider
              operations:
                - type: StaticOperation
                  object_name: player
                  sync_mode:
                    type: Dedupe
                    primary_key: [[name]]
                    cursor: [updated_at]
                  schema:
                    type: object
                    required:
                      - name
                    additionalProperties: true
                    properties:
                      name:
                        type: string
                      updated_at:
                        type: string
                - type: StaticOperation
                  object_name: position
                  sync_mode:
                    type: Append
                  schema:
                    type: object
                    required:
                      - name
                    additionalProperties: true
                    properties:
                      name:
                        type: string
                      side:
                        type: string    
                - type: StaticOperation
                  object_name: coaching_staff
                  sync_mode:
                    type: Overwrite
                  schema:
                    type: object
                    required:
                      - name
                    additionalProperties: true
                    properties:
                      name:
                        type: string
                - type: StaticOperation
                  object_name: stadium
                  sync_mode:
                    type: Update
                  schema:
                    type: object
                    required:
                      - name
                    additionalProperties: true
                    properties:
                      name:
                        type: string
                - type: StaticOperation
                  object_name: team
                  sync_mode:
                    type: SoftDelete
                  schema:
                    type: object
                    required:
                      - name
                    additionalProperties: true
                    properties:
                      name:
                        type: string
        """.trimIndent()
        )

        val expectedOperations =
            listOf<DestinationOperation>(
                DestinationOperation(
                    "player",
                    Dedupe(
                        listOf<List<String>>(listOf<String>("name")),
                        listOf<String>("updated_at")
                    ),
                    ObjectType(
                        properties =
                            linkedMapOf(
                                "name" to FieldType(StringType, true),
                                "updated_at" to FieldType(StringType, true),
                            ),
                        additionalProperties = true,
                        required = listOf("name"),
                    ),
                    matchingKeys = emptyList<List<String>>()
                ),
                DestinationOperation(
                    "position",
                    Append,
                    ObjectType(
                        properties =
                            linkedMapOf(
                                "name" to FieldType(StringType, true),
                                "side" to FieldType(StringType, true),
                            ),
                        additionalProperties = true,
                        required = listOf<String>("name"),
                    ),
                    matchingKeys = emptyList<List<String>>()
                ),
                DestinationOperation(
                    "coaching_staff",
                    Overwrite,
                    ObjectType(
                        properties =
                            linkedMapOf(
                                "name" to FieldType(StringType, true),
                            ),
                        additionalProperties = true,
                        required = listOf<String>("name"),
                    ),
                    matchingKeys = emptyList<List<String>>()
                ),
                DestinationOperation(
                    "stadium",
                    Update,
                    ObjectType(
                        properties =
                            linkedMapOf(
                                "name" to FieldType(StringType, true),
                            ),
                        additionalProperties = true,
                        required = listOf<String>("name"),
                    ),
                    matchingKeys = emptyList<List<String>>()
                ),
                DestinationOperation(
                    "team",
                    SoftDelete,
                    ObjectType(
                        properties =
                            linkedMapOf(
                                "name" to FieldType(StringType, true),
                            ),
                        additionalProperties = true,
                        required = listOf<String>("name"),
                    ),
                    matchingKeys = emptyList<List<String>>()
                ),
            )

        mockkConstructor(BasicAccessAuthenticator::class)
        val config = MockConfig(VALID_API_ID, VALID_API_TOKEN)
        val dlqChecker = mockk<DlqChecker>()
        every { dlqChecker.check(any()) } returns Unit

        val actualOperations =
            DeclarativeDestinationFactory(config).createCompositeOperationsProvider().get()
        assertEquals(expectedOperations, actualOperations)
    }

    private fun mockManifest(manifestContent: String) {
        // Mock ResourceUtils to return our test manifest
        mockkStatic("io.airbyte.cdk.util.ResourceUtils")
        every { ResourceUtils.readResource("manifest.yaml") } returns manifestContent
    }
}
