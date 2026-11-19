/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.gcs_v2

import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.command.ValidatedJsonUtils
import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.command.gcs.GcsHmacKeyConfiguration
import io.airbyte.cdk.load.command.gcs.GcsWorkloadIdentityFederationConfiguration
import io.mockk.every
import io.mockk.mockk
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.assertThrows

/**
 * Parses a config the way the CDK does (validated against the generated spec schema) and runs it
 * through [GcsV2ConfigurationFactory], for each option of the `credential` dropdown.
 */
class GcsV2ConfigurationFactoryTest {
    private val factory =
        GcsV2ConfigurationFactory(
            mockk<DestinationCatalog> { every { streams } returns emptyList() },
        )

    private fun make(credential: String): GcsV2Configuration<*> =
        factory.makeWithoutExceptionHandling(
            ValidatedJsonUtils.parseOne(
                GcsV2Specification::class.java,
                """{"gcs_bucket_name":"my-bucket","gcs_bucket_path":"out","gcs_bucket_region":"europe-north1",""" +
                    """"format":{"format_type":"JSONL"},"credential":$credential}""",
            ),
        )

    private val wifCredential =
        """{"type":"external_account",""" +
            """"audience":"//iam.googleapis.com/projects/1/locations/global/workloadIdentityPools/p/providers/q",""" +
            """"subject_token_type":"urn:ietf:params:oauth:token-type:jwt",""" +
            """"token_url":"https://sts.googleapis.com/v1/token",""" +
            """"credential_source":{"file":"/var/run/token"}}"""

    @Test
    fun `HMAC key option builds the HMAC client configuration`() {
        val config =
            make(
                """{"credential_type":"HMAC_KEY","hmac_key_access_id":"id","hmac_key_secret":"secret"}""",
            )

        assertEquals(
            GcsHmacKeyConfiguration("id", "secret"),
            config.gcsClientConfiguration.credential,
        )
        assertEquals("my-bucket", config.gcsClientConfiguration.gcsBucketName)
        assertEquals("out", config.gcsClientConfiguration.path)
        assertEquals("europe-north1", config.gcsClientConfiguration.region)
    }

    @Test
    fun `HMAC key option rejects a blank key`() {
        assertThrows<ConfigErrorException> {
            make("""{"credential_type":"HMAC_KEY","hmac_key_access_id":"","hmac_key_secret":"s"}""")
        }
    }

    @Test
    fun `Workload Identity Federation option builds the WIF client configuration`() {
        val config =
            make(
                """{"credential_type":"WORKLOAD_IDENTITY_FEDERATION","credentials_json":${quote(wifCredential)}}""",
            )

        assertEquals(
            GcsWorkloadIdentityFederationConfiguration(wifCredential),
            config.gcsClientConfiguration.credential,
        )
        assertEquals("my-bucket", config.gcsClientConfiguration.gcsBucketName)
    }

    @Test
    fun `Workload Identity Federation option rejects a service account key`() {
        val key = """{"type":"service_account","client_email":"x@y.iam.gserviceaccount.com"}"""
        val e =
            assertThrows<ConfigErrorException> {
                make(
                    """{"credential_type":"WORKLOAD_IDENTITY_FEDERATION","credentials_json":${quote(key)}}""",
                )
            }
        assertTrue(e.message!!.contains("external_account"))
    }

    @Test
    fun `spec offers both credential options`() {
        val oneOf =
            ValidatedJsonUtils.generateAirbyteJsonSchema(GcsV2Specification::class.java)
                .at("/properties/credential/oneOf")
        val types = oneOf.map { it.at("/properties/credential_type/enum/0").asText() }
        val titles = oneOf.map { it.get("title").asText() }

        assertEquals(listOf("HMAC_KEY", "WORKLOAD_IDENTITY_FEDERATION"), types)
        assertEquals(listOf("HMAC key", "Workload Identity Federation"), titles)
    }

    private fun quote(s: String) = "\"" + s.replace("\"", "\\\"") + "\""
}
