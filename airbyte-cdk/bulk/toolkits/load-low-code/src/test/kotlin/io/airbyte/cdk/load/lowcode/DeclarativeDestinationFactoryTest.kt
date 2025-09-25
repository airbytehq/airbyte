/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.lowcode

import com.fasterxml.jackson.databind.ObjectMapper
import io.airbyte.cdk.load.check.dlq.DlqChecker
import io.airbyte.cdk.load.command.Append
import io.airbyte.cdk.load.command.Dedupe
import io.airbyte.cdk.load.command.DestinationOperation
import io.airbyte.cdk.load.command.SoftDelete
import io.airbyte.cdk.load.command.Update
import io.airbyte.cdk.load.data.FieldType
import io.airbyte.cdk.load.data.ObjectType
import io.airbyte.cdk.load.data.StringType
import io.airbyte.cdk.load.http.authentication.BasicAccessAuthenticator
import io.airbyte.cdk.load.model.checker.HttpRequestChecker
import io.airbyte.cdk.load.model.destination_import_mode.Insert as InsertModel
import io.airbyte.cdk.load.model.destination_import_mode.SoftDelete as SoftDeleteModel
import io.airbyte.cdk.load.model.destination_import_mode.Update as UpdateModel
import io.airbyte.cdk.load.model.destination_import_mode.Upsert as UpsertModel
import io.airbyte.cdk.load.model.discover.CatalogOperation
import io.airbyte.cdk.load.model.discover.CompositeCatalogOperations
import io.airbyte.cdk.load.model.discover.StaticCatalogOperation
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
import org.junit.jupiter.api.AfterEach
import org.junit.jupiter.api.Test

val VALID_API_ID: String = "api_id"
val VALID_API_TOKEN: String = "api_token"

class DeclarativeDestinationFactoryTest {

    @AfterEach
    fun tearDown() {
        unmockkStatic("io.airbyte.cdk.util.ResourceUtils")
    }

    @Test
    internal fun `test when check then ensure check gets interpolated credentials`() {
        val mapper = ObjectMapper()

        val config =
            Jsons.readTree("""{"api_id": "$VALID_API_ID", "api_token": "$VALID_API_TOKEN"}""")

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
                .withCompositeOperation(
                    CompositeCatalogOperations(
                        operations =
                            listOf<CatalogOperation>(
                                StaticCatalogOperation(
                                    objectName = "player",
                                    destinationImportMode = UpsertModel,
                                    schema =
                                        mapper.valueToTree(
                                            mapOf(
                                                "type" to "object",
                                                "required" to listOf("name"),
                                                "additionalProperties" to true,
                                                "properties" to
                                                    mapOf(
                                                        "name" to mapOf("type" to "string"),
                                                        "updated_at" to mapOf("type" to "string")
                                                    )
                                            )
                                        ),
                                    matchingKeys = listOf(listOf("test"))
                                )
                            )
                    )
                )
                .build()
        )

        mockkConstructor(BasicAccessAuthenticator::class)
        val dlqChecker = mockk<DlqChecker>()
        every { dlqChecker.check(any()) } returns Unit

        DeclarativeDestinationFactory(config).createDestinationChecker(dlqChecker).check()

        verify {
            constructedWith<BasicAccessAuthenticator>(
                    EqMatcher(VALID_API_ID),
                    EqMatcher(VALID_API_TOKEN)
                )
                .intercept(any())
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
    }

    @Test
    internal fun `test static operations with all sync modes`() {
        val mapper = ObjectMapper()

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
                .withCompositeOperation(
                    CompositeCatalogOperations(
                        operations =
                            listOf<CatalogOperation>(
                                StaticCatalogOperation(
                                    objectName = "player",
                                    destinationImportMode = UpsertModel,
                                    schema =
                                        mapper.valueToTree(
                                            mapOf(
                                                "type" to "object",
                                                "required" to listOf("name"),
                                                "additionalProperties" to true,
                                                "properties" to
                                                    mapOf(
                                                        "name" to mapOf("type" to "string"),
                                                        "updated_at" to mapOf("type" to "string")
                                                    )
                                            )
                                        )
                                ),
                                StaticCatalogOperation(
                                    objectName = "position",
                                    destinationImportMode = InsertModel,
                                    schema =
                                        mapper.valueToTree(
                                            mapOf(
                                                "type" to "object",
                                                "required" to listOf("name"),
                                                "additionalProperties" to true,
                                                "properties" to
                                                    mapOf(
                                                        "name" to mapOf("type" to "string"),
                                                        "side" to mapOf("type" to "string")
                                                    )
                                            )
                                        )
                                ),
                                StaticCatalogOperation(
                                    objectName = "stadium",
                                    destinationImportMode = UpdateModel,
                                    schema =
                                        mapper.valueToTree(
                                            mapOf(
                                                "type" to "object",
                                                "required" to listOf("name"),
                                                "additionalProperties" to true,
                                                "properties" to
                                                    mapOf("name" to mapOf("type" to "string"))
                                            )
                                        )
                                ),
                                StaticCatalogOperation(
                                    objectName = "team",
                                    destinationImportMode = SoftDeleteModel,
                                    schema =
                                        mapper.valueToTree(
                                            mapOf(
                                                "type" to "object",
                                                "required" to listOf("name"),
                                                "additionalProperties" to true,
                                                "properties" to
                                                    mapOf("name" to mapOf("type" to "string"))
                                            )
                                        )
                                )
                            )
                    )
                )
                .build()
        )

        val expectedOperations =
            listOf(
                DestinationOperation(
                    "player",
                    Dedupe(emptyList(), emptyList()),
                    ObjectType(
                        properties =
                            linkedMapOf(
                                "name" to FieldType(StringType, true),
                                "updated_at" to FieldType(StringType, true),
                            ),
                        additionalProperties = true,
                        required = listOf("name"),
                    ),
                    matchingKeys = emptyList()
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
                        required = listOf("name"),
                    ),
                    matchingKeys = emptyList()
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
                        required = listOf("name"),
                    ),
                    matchingKeys = emptyList()
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
                        required = listOf("name"),
                    ),
                    matchingKeys = emptyList()
                ),
            )

        mockkConstructor(BasicAccessAuthenticator::class)
        val config =
            Jsons.readTree("""{"api_id": "$VALID_API_ID", "api_token": "$VALID_API_TOKEN"}""")

        val actualOperations = DeclarativeDestinationFactory(config).createOperationProvider().get()
        assertEquals(expectedOperations, actualOperations)
    }

    private fun mockManifest(manifestContent: String) {
        // Mock ResourceUtils to return our test manifest
        mockkStatic("io.airbyte.cdk.util.ResourceUtils")
        every { ResourceUtils.readResource("manifest.yaml") } returns manifestContent
    }
}
