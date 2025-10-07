/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.lowcode

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.ObjectMapper
import io.airbyte.cdk.load.check.dlq.DlqChecker
import io.airbyte.cdk.load.command.Append
import io.airbyte.cdk.load.command.Dedupe
import io.airbyte.cdk.load.command.DestinationOperation
import io.airbyte.cdk.load.command.SoftDelete
import io.airbyte.cdk.load.command.Update
import io.airbyte.cdk.load.data.BooleanType
import io.airbyte.cdk.load.data.FieldType
import io.airbyte.cdk.load.data.NumberType
import io.airbyte.cdk.load.data.ObjectType
import io.airbyte.cdk.load.data.StringType
import io.airbyte.cdk.load.http.HttpRequester
import io.airbyte.cdk.load.http.Response
import io.airbyte.cdk.load.http.authentication.BasicAccessAuthenticator
import io.airbyte.cdk.load.model.checker.HttpRequestChecker
import io.airbyte.cdk.load.model.destination_import_mode.Insert as InsertModel
import io.airbyte.cdk.load.model.destination_import_mode.SoftDelete as SoftDeleteModel
import io.airbyte.cdk.load.model.destination_import_mode.Update as UpdateModel
import io.airbyte.cdk.load.model.destination_import_mode.Upsert as UpsertModel
import io.airbyte.cdk.load.model.discover.ArrayType as ArrayTypeModel
import io.airbyte.cdk.load.model.discover.BooleanType as BooleanTypeModel
import io.airbyte.cdk.load.model.discover.CatalogOperation
import io.airbyte.cdk.load.model.discover.CompositeCatalogOperations
import io.airbyte.cdk.load.model.discover.DynamicCatalogOperation
import io.airbyte.cdk.load.model.discover.DynamicDestinationObjects
import io.airbyte.cdk.load.model.discover.FieldType as FieldTypeModel
import io.airbyte.cdk.load.model.discover.InsertionMethod
import io.airbyte.cdk.load.model.discover.NumberType as NumberTypeModel
import io.airbyte.cdk.load.model.discover.SchemaConfiguration
import io.airbyte.cdk.load.model.discover.StaticCatalogOperation
import io.airbyte.cdk.load.model.discover.StaticDestinationObjects
import io.airbyte.cdk.load.model.discover.StringType as StringTypeModel
import io.airbyte.cdk.load.model.discover.TypesMap
import io.airbyte.cdk.load.model.http.HttpMethod
import io.airbyte.cdk.load.model.http.HttpRequester as HttpRequesterModel
import io.airbyte.cdk.load.model.http.authenticator.BasicAccessAuthenticator as BasicAccessAuthenticatorModel
import io.airbyte.cdk.load.model.retriever.Retriever
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
val ANY_CONFIG: JsonNode = convertMapToJsonNode(emptyMap())

class DeclarativeDestinationFactoryTest {

    @Test
    internal fun `test when check then ensure check gets interpolated credentials`() {
        val mapper = ObjectMapper()

        val config =
            Jsons.readTree("""{"api_id": "$VALID_API_ID", "api_token": "$VALID_API_TOKEN"}""")

        mockManifest(
            ManifestBuilder()
                .withChecker(
                    HttpRequestChecker(
                        HttpRequesterModel(
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
                .withCatalogOperation(
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

        try {
            DeclarativeDestinationFactory(config).createDestinationChecker(dlqChecker).check()

            verify {
                constructedWith<BasicAccessAuthenticator>(
                        EqMatcher(VALID_API_ID),
                        EqMatcher(VALID_API_TOKEN)
                    )
                    .intercept(any())
            }
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
        val mapper = ObjectMapper()

        mockManifest(
            ManifestBuilder()
                .withChecker(
                    HttpRequestChecker(
                        HttpRequesterModel(
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
                .withCatalogOperation(
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

        val actualOperations =
            DeclarativeDestinationFactory(ANY_CONFIG).createOperationProvider().get()
        assertEquals(expectedOperations, actualOperations)
    }

    @Test
    internal fun `test dynamic operations with static destination objects`() {
        val mockedResponse =
            mapOf<String, Any>(
                "properties" to
                    listOf(
                        mapOf("name" to "name", "type" to "string"),
                        mapOf("name" to "breathingForm", "type" to "art"),
                        mapOf("name" to "age", "type" to "numberlike")
                    )
            )

        val objectsResponse: Response = mockk<Response>()
        every { objectsResponse.statusCode } returns 200
        every { objectsResponse.body } returns
            createObjectsResponse(mockedResponse).byteInputStream(Charsets.UTF_8)
        every { objectsResponse.close() } returns Unit

        mockkConstructor(HttpRequester::class)
        every { anyConstructed<HttpRequester>().send(any()) } returns objectsResponse

        mockManifest(
            ManifestBuilder()
                .withCatalogOperation(
                    DynamicCatalogOperation(
                        objects = StaticDestinationObjects(objects = listOf("hashiras")),
                        schema =
                            SchemaConfiguration(
                                propertiesPath = listOf("properties"),
                                propertyNamePath = listOf("name"),
                                typePath = listOf("type"),
                                typeMapping =
                                    listOf(
                                        TypesMap(
                                            apiType = listOf("string", "art"),
                                            airbyteType = listOf(StringTypeModel)
                                        ),
                                        TypesMap(
                                            apiType = listOf("numberlike"),
                                            airbyteType = listOf(NumberTypeModel)
                                        ),
                                        TypesMap(
                                            apiType = listOf("array"),
                                            airbyteType =
                                                listOf(
                                                    ArrayTypeModel(
                                                        items =
                                                            FieldTypeModel(StringTypeModel, true)
                                                    )
                                                )
                                        ),
                                    )
                            ),
                        schemaRetriever =
                            Retriever(
                                httpRequester =
                                    HttpRequesterModel(
                                        url = "https://hashira.net/object_schemas",
                                        method = HttpMethod.GET,
                                        authenticator =
                                            BasicAccessAuthenticatorModel(
                                                username = "username",
                                                password = "password",
                                            )
                                    ),
                                selector = listOf("properties")
                            ),
                        insertionMethods =
                            listOf(
                                InsertionMethod(
                                    destinationImportMode = InsertModel,
                                    availabilityPredicate = "{{ true }}",
                                    matchingKeyPredicate = "{{ property['type'] != 'ignore_me' }}",
                                    requiredPredicate = ""
                                )
                            )
                    )
                )
                .build()
        )

        val expectedOperations =
            listOf(
                DestinationOperation(
                    "hashiras",
                    Append,
                    ObjectType(
                        properties =
                            linkedMapOf(
                                "name" to FieldType(StringType, true),
                                "breathingForm" to FieldType(StringType, true),
                                "age" to FieldType(NumberType, true),
                            ),
                        additionalProperties = false,
                        required = emptyList(),
                    ),
                    matchingKeys = listOf(listOf("name"), listOf("breathingForm"), listOf("age")),
                ),
            )

        try {
            val actualOperations =
                DeclarativeDestinationFactory(ANY_CONFIG).createOperationProvider().get()
            assertEquals(expectedOperations, actualOperations)
        } finally {
            unmockkStatic("io.airbyte.cdk.util.ResourceUtils") // Clean up mocks
        }
    }

    @Test
    internal fun `test dynamic operations with dynamic destination objects`() {
        val objectsMockBody =
            mapOf<String, Any>(
                "results" to
                    listOf(
                        mapOf(
                            "name" to "breathingStyle",
                        ),
                    )
            )

        val schemaMockBody =
            mapOf<String, Any>(
                "properties" to
                    listOf(
                        mapOf("name" to "name", "type" to "string"),
                        mapOf("name" to "isMainStyle", "type" to "bool"),
                        mapOf("name" to "numberOfForms", "type" to "numberlike")
                    )
            )

        val objectsResponse: Response = mockk<Response>()
        every { objectsResponse.statusCode } returns 200
        every { objectsResponse.body } returns
            createObjectsResponse(objectsMockBody).byteInputStream(Charsets.UTF_8)
        every { objectsResponse.close() } returns Unit

        val schemaResponse: Response = mockk<Response>()
        every { schemaResponse.statusCode } returns 200
        every { schemaResponse.body } returns
            createObjectsResponse(schemaMockBody).byteInputStream(Charsets.UTF_8)
        every { schemaResponse.close() } returns Unit

        // Not a fan because this just brute force mocks one request after the other
        mockkConstructor(HttpRequester::class)
        every { anyConstructed<HttpRequester>().send(any()) } returnsMany
            listOf(objectsResponse, schemaResponse)

        // This doesn't quite accurately test the mock based on the incoming url parameter of the
        // constructor, but we can't check the url during send() because its private. Ideally,
        // this should mock based on the url field so we adequately test inputs are sent as
        // expected. but we don't currently have a good mechanism to do so. Leaving a little
        // bit of experimental code for the moment. The mocker is out of scope for the moment
        //        every {
        //            constructedWith<HttpRequester>(
        //                any(),
        //                any(),
        //                EqMatcher("https://hashira.net/objects")
        //            ).send(any())
        //        } returns objectsResponse
        //        every {
        //            constructedWith<HttpRequester>(
        //                any(),
        //                any(),
        //                EqMatcher("https://hashira.net/object_schemas")
        //            ).send(any())
        //        } returns schemaResponse

        mockManifest(
            ManifestBuilder()
                .withCatalogOperation(
                    DynamicCatalogOperation(
                        objects =
                            DynamicDestinationObjects(
                                retriever =
                                    Retriever(
                                        httpRequester =
                                            HttpRequesterModel(
                                                url = "https://hashira.net/objects",
                                                method = HttpMethod.GET,
                                            ),
                                        selector = listOf("results")
                                    ),
                                namePath = listOf("name"),
                            ),
                        schema =
                            SchemaConfiguration(
                                propertiesPath = listOf("properties"),
                                propertyNamePath = listOf("name"),
                                typePath = listOf("type"),
                                typeMapping =
                                    listOf(
                                        TypesMap(
                                            apiType = listOf("string", ""),
                                            airbyteType = listOf(StringTypeModel)
                                        ),
                                        TypesMap(
                                            apiType = listOf("bool"),
                                            airbyteType = listOf(BooleanTypeModel)
                                        ),
                                        TypesMap(
                                            apiType = listOf("numberlike"),
                                            airbyteType = listOf(NumberTypeModel)
                                        ),
                                    )
                            ),
                        schemaRetriever =
                            Retriever(
                                httpRequester =
                                    HttpRequesterModel(
                                        url = "https://hashira.net/object_schemas",
                                        method = HttpMethod.GET,
                                        authenticator =
                                            BasicAccessAuthenticatorModel(
                                                username = "username",
                                                password = "password",
                                            )
                                    ),
                                selector = listOf("properties")
                            ),
                        insertionMethods =
                            listOf(
                                InsertionMethod(
                                    destinationImportMode = InsertModel,
                                    availabilityPredicate = "{{ true }}",
                                    matchingKeyPredicate = "{{ property['type'] != 'ignore_me' }}",
                                    requiredPredicate = ""
                                )
                            )
                    )
                )
                .build()
        )

        val expectedOperations =
            listOf(
                DestinationOperation(
                    "breathingStyle",
                    Append,
                    ObjectType(
                        properties =
                            linkedMapOf(
                                "name" to FieldType(StringType, true),
                                "isMainStyle" to FieldType(BooleanType, true),
                                "numberOfForms" to FieldType(NumberType, true),
                            ),
                        additionalProperties = false,
                        required = emptyList(),
                    ),
                    matchingKeys =
                        listOf(listOf("name"), listOf("isMainStyle"), listOf("numberOfForms")),
                ),
            )

        try {
            val actualOperations =
                DeclarativeDestinationFactory(ANY_CONFIG).createOperationProvider().get()
            assertEquals(expectedOperations, actualOperations)
        } finally {
            unmockkStatic("io.airbyte.cdk.util.ResourceUtils") // Clean up mocks
        }
    }

    private fun mockManifest(manifestContent: String) {
        // Mock ResourceUtils to return our test manifest
        mockkStatic("io.airbyte.cdk.util.ResourceUtils")
        every { ResourceUtils.readResource("manifest.yaml") } returns manifestContent
    }

    private fun createObjectsResponse(responseBody: Map<String, Any>): String {
        return ObjectMapper().writeValueAsString(responseBody)
    }
}

private fun convertMapToJsonNode(map: Map<String, Any>): JsonNode = ObjectMapper().valueToTree(map)
