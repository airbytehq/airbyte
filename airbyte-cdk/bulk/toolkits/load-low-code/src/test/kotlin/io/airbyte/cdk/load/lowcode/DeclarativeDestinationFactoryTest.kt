/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.lowcode

import io.airbyte.cdk.load.check.dlq.DlqChecker
import io.airbyte.cdk.load.command.Append
import io.airbyte.cdk.load.command.Dedupe
import io.airbyte.cdk.load.command.DestinationOperation
import io.airbyte.cdk.load.command.Overwrite
import io.airbyte.cdk.load.command.SoftDelete
import io.airbyte.cdk.load.command.Update
import io.airbyte.cdk.load.data.FieldType
import io.airbyte.cdk.load.data.ObjectType
import io.airbyte.cdk.load.data.StringType
import io.airbyte.cdk.load.http.authentication.BasicAccessAuthenticator
import io.airbyte.cdk.load.model.checker.HttpRequestChecker
import io.airbyte.cdk.load.model.http.HttpMethod
import io.airbyte.cdk.load.model.http.HttpRequester
import io.airbyte.cdk.load.model.http.authenticator.BasicAccessAuthenticator as BasicAccessAuthenticatorModel
import io.airbyte.cdk.load.model.spec.Spec
import io.airbyte.cdk.util.Jsons
import io.airbyte.cdk.util.ResourceUtils
import io.airbyte.protocol.models.v0.AdvancedAuth
import io.mockk.EqMatcher
import io.mockk.every
import io.mockk.mockk
import io.mockk.mockkConstructor
import io.mockk.mockkStatic
import io.mockk.unmockkStatic
import io.mockk.verify
import kotlin.test.assertEquals
import kotlin.test.assertNotNull
import org.junit.jupiter.api.Test

val VALID_API_ID: String = "api_id"
val VALID_API_TOKEN: String = "api_token"

class DeclarativeDestinationFactoryTest {

    @Test
    internal fun `test when check then ensure check gets interpolated credentials`() {
        mockManifest(
            ManifestBuilder()
                .withChecker(
                    HttpRequestChecker(
                        HttpRequester(
                            url = "https://airbyte.io/",
                            method = HttpMethod.GET,
                            authenticator =
                                BasicAccessAuthenticatorModel(
                                    """{{ config["api_id"] }}""",
                                    """{{ config["api_token"] }}""",
                                ),
                        ),
                    )
                )
                .withDiscovery()
                .build()
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
        val dlqChecker = mockk<DlqChecker>()
        every { dlqChecker.check(any()) } returns Unit

        try {
            DeclarativeDestinationFactory(
                    Jsons.readTree(
                        """{"api_id": "$VALID_API_ID", "api_token": "$VALID_API_TOKEN"}"""
                    )
                )
                .createDestinationChecker(dlqChecker)
                .check()

            verify {
                constructedWith<BasicAccessAuthenticator>(
                        EqMatcher(VALID_API_ID),
                        EqMatcher(VALID_API_TOKEN)
                    )
                    .intercept(any())
            }

            val actualOperations =
                DeclarativeDestinationFactory(config).createOperationProvider().get()
            assertEquals(expectedOperations, actualOperations)
        } finally {
            unmockkStatic("io.airbyte.cdk.util.ResourceUtils") // Clean up mocks
        }
    }

    @Test
    internal fun `test when create specification then add object storage to connection specification`() {
        val advancedAuth = AdvancedAuth().withPredicateValue("a predicate value")
        mockManifest(
            ManifestBuilder()
                .withSpec(
                    Spec(
                        connectionSpecification =
                            Jsons.readTree(
                                """{"type":"object","${'$'}schema":"http://json-schema.org/draft-07/schema#","required":["account_id"],"properties":{"account_id":{"type":"string","order":0,"airbyte_secret":true}}}"""
                            ),
                        advancedAuth = advancedAuth,
                    )
                )
                .build()
        )

        val spec =
            DeclarativeDestinationFactory(Jsons.readTree("""{"account_id": "an_account_id"}"""))
                .createSpecificationFactory()
                .create()

        assertNotNull(spec.connectionSpecification.get("properties").get("account_id"))
        assertNotNull(spec.connectionSpecification.get("properties").get("object_storage_config"))
        assertEquals(advancedAuth, spec.advancedAuth)

        unmockkStatic("io.airbyte.cdk.util.ResourceUtils")
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
              type: CompositeOperations
              operations:
                - type: StaticOperation
                  object_name: player
                  destination_import_mode:
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
                  destination_import_mode:
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
                  destination_import_mode:
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
                  destination_import_mode:
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
                  destination_import_mode:
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

        val actualOperations = DeclarativeDestinationFactory(config).createOperationProvider().get()
        assertEquals(expectedOperations, actualOperations)
    }

    private fun mockManifest(manifestContent: String) {
        // Mock ResourceUtils to return our test manifest
        mockkStatic("io.airbyte.cdk.util.ResourceUtils")
        every { ResourceUtils.readResource("manifest.yaml") } returns manifestContent
    }
}
