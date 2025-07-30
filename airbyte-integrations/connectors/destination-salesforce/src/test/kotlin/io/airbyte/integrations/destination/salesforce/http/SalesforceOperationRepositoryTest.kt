/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.salesforce.http

import io.airbyte.cdk.load.command.Append
import io.airbyte.cdk.load.command.Dedupe
import io.airbyte.cdk.load.command.SoftDelete
import io.airbyte.cdk.load.command.Update
import io.airbyte.cdk.load.data.ObjectType
import io.airbyte.cdk.load.http.HttpClient
import io.airbyte.cdk.load.http.Request
import io.airbyte.cdk.load.http.RequestMethod
import io.airbyte.cdk.load.http.Response
import io.airbyte.integrations.destination.salesforce.io.airbyte.integrations.destination.salesforce.http.SalesforceOperationRepository
import io.mockk.every
import io.mockk.mockk
import java.io.InputStream
import java.lang.IllegalStateException
import kotlin.test.assertEquals
import kotlin.test.assertFailsWith
import kotlin.test.assertFalse
import kotlin.test.assertIs
import kotlin.test.assertTrue
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test

class SalesforceOperationRepositoryTest {
    private val BASE_URL = "https://base-url.com"
    private lateinit var httpClient: HttpClient
    private lateinit var repo: SalesforceOperationRepository

    @BeforeEach
    fun setUp() {
        httpClient = mockk()
        repo = SalesforceOperationRepository(httpClient) { BASE_URL }
    }

    @Test
    internal fun `test given object is createable when fetch all then return create operation`() {
        every {
            httpClient.send(
                Request(method = RequestMethod.GET, url = "$BASE_URL/services/data/v62.0/sobjects")
            )
        } returns aResponse(200, SalesforceSObjectsResponseBuilder().withObject("Contact").build())
        every {
            httpClient.send(
                Request(
                    method = RequestMethod.GET,
                    url = "$BASE_URL/services/data/v62.0/sobjects/Contact/describe"
                )
            )
        } returns
            aResponse(
                200,
                SalesforceSObjectDescribeResponseBuilder()
                    .withName("Contact")
                    .withCreateable(true)
                    .withField(
                        SalesforceFieldBuilder()
                            .withName("createableField")
                            .withCreateable(true)
                            .withDefaultedOnCreate(true)
                    )
                    .build()
            )

        val operations = repo.fetchAll()

        assertEquals(1, operations.size)
        val operation = operations[0]
        assertEquals(Append, operation.syncMode)
        assertEquals(1, operation.schema.asColumns().size)
        assertEquals(emptyList<List<String>>(), operation.matchingKeys)
        assertIs<ObjectType>(operation.schema)
        val schema = operation.schema as ObjectType
        assertFalse(schema.additionalProperties)
        assertEquals(emptyList(), schema.required)
    }

    @Test
    internal fun `test given object is updateable when fetch all then return update operation`() {
        every {
            httpClient.send(
                Request(method = RequestMethod.GET, url = "$BASE_URL/services/data/v62.0/sobjects")
            )
        } returns aResponse(200, SalesforceSObjectsResponseBuilder().withObject("Contact").build())
        every {
            httpClient.send(
                Request(
                    method = RequestMethod.GET,
                    url = "$BASE_URL/services/data/v62.0/sobjects/Contact/describe"
                )
            )
        } returns
            aResponse(
                200,
                SalesforceSObjectDescribeResponseBuilder()
                    .withName("Contact")
                    .withUpdateable(true)
                    .withField(
                        SalesforceFieldBuilder().withName("updateableField").withUpdateable(true)
                    )
                    .withField(
                        SalesforceFieldBuilder()
                            .withName("externalIdFieldOnlyAMatcherInUpsert")
                            .withUpdateable(true)
                            .withExternalId(true)
                    )
                    .build()
            )
        val operations = repo.fetchAll()

        assertEquals(1, operations.size)
        val operation = operations[0]
        assertEquals(Update, operation.syncMode)
        assertEquals(2, operation.schema.asColumns().size)
        assertEquals(listOf<List<String>>(listOf<String>("Id")), operation.matchingKeys)
        assertIs<ObjectType>(operation.schema)
        val schema = operation.schema as ObjectType
        assertFalse(schema.additionalProperties)
        assertEquals(emptyList<String>(), schema.required)
    }

    @Test
    internal fun `test given object is createable and updateable when fetch all then return create, update and upsert operation`() {
        every {
            httpClient.send(
                Request(method = RequestMethod.GET, url = "$BASE_URL/services/data/v62.0/sobjects")
            )
        } returns aResponse(200, SalesforceSObjectsResponseBuilder().withObject("Contact").build())
        every {
            httpClient.send(
                Request(
                    method = RequestMethod.GET,
                    url = "$BASE_URL/services/data/v62.0/sobjects/Contact/describe"
                )
            )
        } returns
            aResponse(
                200,
                SalesforceSObjectDescribeResponseBuilder()
                    .withName("Contact")
                    .withCreateable(true)
                    .withUpdateable(true)
                    .withField(
                        SalesforceFieldBuilder()
                            .withName("upsertableField")
                            .withCreateable(true)
                            .withUpdateable(true)
                            .withDefaultedOnCreate(true)
                    )
                    .withField(
                        SalesforceFieldBuilder()
                            .withName("createableField")
                            .withCreateable(true)
                            .withUpdateable(false)
                    )
                    .withField(
                        SalesforceFieldBuilder()
                            .withName("updateableField")
                            .withCreateable(false)
                            .withUpdateable(true)
                    )
                    .withField(
                        SalesforceFieldBuilder()
                            .withName("matchingField")
                            .withCreateable(false)
                            .withUpdateable(false)
                            .withExternalId(true)
                    )
                    .build()
            )
        val operations = repo.fetchAll()

        assertEquals(3, operations.size)
        val upsertOperations =
            operations.filter { it.syncMode == Dedupe(emptyList(), emptyList()) }.toList()
        assertEquals(1, upsertOperations.size)
        val operation = upsertOperations[0]
        assertEquals(Dedupe(emptyList(), emptyList()), operation.syncMode)
        assertEquals(
            listOf("upsertableField", "matchingField"),
            operation.schema.asColumns().map { it.key }
        )
        assertEquals(listOf<List<String>>(listOf<String>("matchingField")), operation.matchingKeys)
        assertIs<ObjectType>(operation.schema)
        val schema = operation.schema as ObjectType
        assertFalse(schema.additionalProperties)
        assertEquals(emptyList(), schema.required)
    }

    @Test
    internal fun `test given object is createable and updateable but not external id when fetch all then do not return dedup operation`() {
        every {
            httpClient.send(
                Request(method = RequestMethod.GET, url = "$BASE_URL/services/data/v62.0/sobjects")
            )
        } returns aResponse(200, SalesforceSObjectsResponseBuilder().withObject("Contact").build())
        every {
            httpClient.send(
                Request(
                    method = RequestMethod.GET,
                    url = "$BASE_URL/services/data/v62.0/sobjects/Contact/describe"
                )
            )
        } returns
            aResponse(
                200,
                SalesforceSObjectDescribeResponseBuilder()
                    .withName("Contact")
                    .withCreateable(true)
                    .withUpdateable(true)
                    .withField(
                        SalesforceFieldBuilder()
                            .withName("createableField")
                            .withCreateable(true)
                            .withUpdateable(true)
                    )
                    .build()
            )
        val operations = repo.fetchAll()

        assertEquals(2, operations.size)
        val upsertOperations =
            operations.filter { it.syncMode == Dedupe(emptyList(), emptyList()) }.toList()
        assertTrue(upsertOperations.isEmpty())
    }

    @Test
    internal fun `test given object is deleteable when fetch all then return delete operation`() {
        every {
            httpClient.send(
                Request(method = RequestMethod.GET, url = "$BASE_URL/services/data/v62.0/sobjects")
            )
        } returns aResponse(200, SalesforceSObjectsResponseBuilder().withObject("Contact").build())
        every {
            httpClient.send(
                Request(
                    method = RequestMethod.GET,
                    url = "$BASE_URL/services/data/v62.0/sobjects/Contact/describe"
                )
            )
        } returns
            aResponse(
                200,
                SalesforceSObjectDescribeResponseBuilder()
                    .withName("Contact")
                    .withDeletable(true)
                    .withField(SalesforceFieldBuilder().withName("Id"))
                    .build()
            )

        val operations = repo.fetchAll()

        assertEquals(1, operations.size)
        val operation = operations[0]
        assertEquals(SoftDelete, operation.syncMode)
        assertEquals(listOf<List<String>>(listOf<String>("Id")), operation.matchingKeys)
        assertEquals(1, operation.schema.asColumns().size)
    }

    @Test
    internal fun `test given many objects when fetch all then create operations for all objects`() {
        every {
            httpClient.send(
                Request(method = RequestMethod.GET, url = "$BASE_URL/services/data/v62.0/sobjects")
            )
        } returns
            aResponse(
                200,
                SalesforceSObjectsResponseBuilder().withObject("Contact").withObject("Lead").build()
            )
        every {
            httpClient.send(
                Request(
                    method = RequestMethod.GET,
                    url = "$BASE_URL/services/data/v62.0/sobjects/Contact/describe"
                )
            )
        } returns
            aResponse(
                200,
                SalesforceSObjectDescribeResponseBuilder()
                    .withName("Contact")
                    .withDeletable(true)
                    .withField(SalesforceFieldBuilder().withName("Id"))
                    .build()
            )
        every {
            httpClient.send(
                Request(
                    method = RequestMethod.GET,
                    url = "$BASE_URL/services/data/v62.0/sobjects/Lead/describe"
                )
            )
        } returns
            aResponse(
                200,
                SalesforceSObjectDescribeResponseBuilder()
                    .withName("Lead")
                    .withDeletable(true)
                    .withField(SalesforceFieldBuilder().withName("Id"))
                    .build()
            )

        val operations = repo.fetchAll()

        assertTrue { operations.map { it.objectName }.containsAll(setOf("Contact", "Lead")) }
    }

    @Test
    internal fun `test given unsupported status code on objects when fetch all then raise exception`() {
        every {
            httpClient.send(
                Request(method = RequestMethod.GET, url = "$BASE_URL/services/data/v62.0/sobjects")
            )
        } returns aResponse(500, "any body".byteInputStream())

        assertFailsWith<IllegalStateException>(block = { repo.fetchAll() })
    }

    @Test
    internal fun `test given unsupported status code on describe when fetch all then raise exception`() {
        every {
            httpClient.send(
                Request(method = RequestMethod.GET, url = "$BASE_URL/services/data/v62.0/sobjects")
            )
        } returns aResponse(200, SalesforceSObjectsResponseBuilder().withObject("Contact").build())
        every {
            httpClient.send(
                Request(
                    method = RequestMethod.GET,
                    url = "$BASE_URL/services/data/v62.0/sobjects/Contact/describe"
                )
            )
        } returns aResponse(500, "any body".byteInputStream())

        assertFailsWith<IllegalStateException>(block = { repo.fetchAll() })
    }

    fun aResponse(statusCode: Int, body: InputStream): Response {
        val response = mockk<Response>()
        every { response.statusCode } returns statusCode
        every { response.body } returns body
        every { response.close() } returns Unit
        return response
    }
}
