/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.dynamodb

import io.airbyte.cdk.util.Jsons
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test
import software.amazon.awssdk.services.dynamodb.DynamoDbClient

class DynamoDbClientFactoryTest {

    private fun configuration(): DynamoDbSourceConfiguration =
        DynamoDbSourceConfigurationFactory()
            .makeWithoutExceptionHandling(
                Jsons.readValue(
                    """
{
  "credentials": {"auth_type": "User", "access_key_id": "AKIA123", "secret_access_key": "s3cr3t"},
  "endpoint": "http://localhost:8000",
  "region": "us-east-2"
}
""",
                    DynamoDbSourceConfigurationSpecification::class.java,
                ),
            )

    /**
     * Every request asks DynamoDB for a gzipped response: a 1 MB `Scan` page is mostly transfer
     * time, and the SDK's HTTP client inflates the body transparently.
     */
    @Test
    fun testClientRequestsGzipResponses() {
        val client: DynamoDbClient = DynamoDbClientFactory.create(configuration())
        client.use {
            val headers: Map<String, List<String>> =
                it.serviceClientConfiguration().overrideConfiguration().headers()
            Assertions.assertEquals(
                listOf(DynamoDbClientFactory.GZIP_ENCODING),
                headers[DynamoDbClientFactory.ACCEPT_ENCODING_HEADER],
            )
        }
    }
}
