/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.hubspot.http

import io.airbyte.cdk.load.command.Dedupe
import io.airbyte.cdk.load.command.DestinationOperation
import io.airbyte.cdk.load.data.ObjectType
import io.airbyte.cdk.load.http.HttpClient
import io.airbyte.cdk.load.http.Request
import io.airbyte.cdk.load.http.RequestMethod
import io.airbyte.cdk.load.http.Response
import io.mockk.every
import io.mockk.mockk
import java.io.InputStream
import kotlin.test.assertEquals
import kotlin.test.assertIs
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test

class HubSpotOperationRepositoryTest {
    private lateinit var httpClient: HttpClient
    private lateinit var repo: HubSpotOperationRepository

    @BeforeEach
    fun setUp() {
        httpClient = mockk()
        mockOtherObjectsAsEmpty()
        repo = HubSpotOperationRepository(httpClient)
    }

    private fun mockOtherObjectsAsEmpty() {
        // custom objects
        every {
            httpClient.send(
                Request(method = RequestMethod.GET, url = "https://api.hubapi.com/crm/v3/schemas")
            )
        } answers
            {
                aResponse(
                    200,
                    HubSpotCustomObjectSchemaResponseBuilder()
                        .withResult(anUnavailableObject())
                        .build()
                )
            }

        // other standard objects (Properties API)
        every {
            httpClient.send(
                Request(
                    method = RequestMethod.GET,
                    url = "https://api.hubapi.com/crm/v3/properties/COMPANY"
                )
            )
        } returns (aResponse(200, anUnavailablePropertiesApiObject().build()))
        every {
            httpClient.send(
                Request(
                    method = RequestMethod.GET,
                    url = "https://api.hubapi.com/crm/v3/properties/DEAL"
                )
            )
        } returns (aResponse(200, anUnavailablePropertiesApiObject().build()))
        every {
            httpClient.send(
                Request(
                    method = RequestMethod.GET,
                    url = "https://api.hubapi.com/crm/v3/properties/PRODUCT"
                )
            )
        } returns (aResponse(200, anUnavailablePropertiesApiObject().build()))
    }

    @Test
    internal fun `test when fetch all then return contact dedupe`() {
        every {
            httpClient.send(
                Request(
                    method = RequestMethod.GET,
                    url = "https://api.hubapi.com/crm/v3/properties/CONTACT"
                )
            )
        } returns aResponse(200, aPropertiesApiResponseWithEmailProperty().build())

        val operations = repo.fetchAll()

        assertEquals(1, operations.size)
        val operation = operations[0]
        assertEquals(Dedupe(emptyList(), emptyList()), operation.syncMode)
        assertEquals(1, operation.schema.asColumns().size)
        assertEquals(listOf(listOf("email")), operation.matchingKeys)
        assertSchemaWithProperties(operations[0], setOf("email"))
    }

    @Test
    internal fun `test given when fetch all then return available fields as part of schema`() {
        every {
            httpClient.send(
                Request(
                    method = RequestMethod.GET,
                    url = "https://api.hubapi.com/crm/v3/properties/CONTACT"
                )
            )
        } returns
            aResponse(
                200,
                aPropertiesApiResponseWithEmailProperty()
                    .withProperty(anAvailableProperty("available"))
                    .build()
            )

        val operations = repo.fetchAll()

        assertEquals(1, operations.size)
        assertSchemaWithProperties(operations[0], setOf("email", "available"))
    }

    @Test
    internal fun `test given calculated field when fetch all then field is not part of schema`() {
        every {
            httpClient.send(
                Request(
                    method = RequestMethod.GET,
                    url = "https://api.hubapi.com/crm/v3/properties/CONTACT"
                )
            )
        } returns
            aResponse(
                200,
                aPropertiesApiResponseWithEmailProperty()
                    .withProperty(aProperty("notAvailable").withCalculated(true))
                    .build()
            )

        val operations = repo.fetchAll()

        assertEquals(1, operations.size)
        assertSchemaWithProperties(operations[0], setOf("email"))
    }

    @Test
    internal fun `test given read only field when fetch all then field is not part of schema`() {
        every {
            httpClient.send(
                Request(
                    method = RequestMethod.GET,
                    url = "https://api.hubapi.com/crm/v3/properties/CONTACT"
                )
            )
        } returns
            aResponse(
                200,
                aPropertiesApiResponseWithEmailProperty()
                    .withProperty(aProperty("notAvailable").withReadOnlyValue(true))
                    .build()
            )

        val operations = repo.fetchAll()

        assertEquals(1, operations.size)
        assertSchemaWithProperties(operations[0], setOf("email"))
    }

    @Test
    internal fun `test given hubspot internal type when fetch all then field is not part of schema`() {
        every {
            httpClient.send(
                Request(
                    method = RequestMethod.GET,
                    url = "https://api.hubapi.com/crm/v3/properties/CONTACT"
                )
            )
        } returns
            aResponse(
                200,
                aPropertiesApiResponseWithEmailProperty()
                    .withProperty(aProperty("notAvailable").withType("object_coordinates"))
                    .build()
            )

        val operations = repo.fetchAll()

        assertEquals(1, operations.size)
        assertSchemaWithProperties(operations[0], setOf("email"))
    }

    @Test
    internal fun `test deal with hasUniqueValue property is discovered`() {
        every {
            httpClient.send(
                Request(
                    method = RequestMethod.GET,
                    url = "https://api.hubapi.com/crm/v3/properties/CONTACT"
                )
            )
        } returns aResponse(200, aPropertiesApiResponseWithEmailProperty().build())
        every {
            httpClient.send(
                Request(
                    method = RequestMethod.GET,
                    url = "https://api.hubapi.com/crm/v3/properties/DEAL"
                )
            )
        } returns
            aResponse(
                200,
                HubSpotPropertiesApiResponseBuilder()
                    .withProperty(anAvailableProperty("deal_unique_id").withHasUniqueValue(true))
                    .build()
            )

        val operations = repo.fetchAll()

        assertEquals(2, operations.size)
        val dealOperation = operations.first { it.objectName == "DEAL" }
        assertEquals(Dedupe(emptyList(), emptyList()), dealOperation.syncMode)
        assertEquals(listOf(listOf("deal_unique_id")), dealOperation.matchingKeys)
        assertSchemaWithProperties(dealOperation, setOf("deal_unique_id"))
    }

    private fun anAvailableProperty(name: String): HubSpotPropertySchemaBuilder =
        aProperty(name).withType("string").withCalculated(false).withReadOnlyValue(false)

    private fun assertSchemaWithProperties(operation: DestinationOperation, fields: Set<String>) {
        assertIs<ObjectType>(operation.schema)

        val schema = operation.schema as ObjectType
        assertEquals(fields, schema.properties.keys)
    }

    private fun aPropertiesApiResponseWithEmailProperty(): HubSpotPropertiesApiResponseBuilder =
        HubSpotPropertiesApiResponseBuilder().withProperty(anAvailableProperty("email"))

    private fun aProperty(name: String): HubSpotPropertySchemaBuilder =
        HubSpotPropertySchemaBuilder().withName(name)

    fun aResponse(statusCode: Int, body: InputStream): Response {
        val response = mockk<Response>()
        every { response.statusCode } returns statusCode
        every { response.body } returns body
        every { response.close() } returns Unit
        return response
    }

    private fun anUnavailableObject(): HubSpotSchemaResponseBuilder =
        HubSpotSchemaResponseBuilder().withName("unavailable")

    private fun anUnavailablePropertiesApiObject(): HubSpotPropertiesApiResponseBuilder =
        HubSpotPropertiesApiResponseBuilder()
}
