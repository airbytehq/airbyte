/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.command.gcs

import io.airbyte.cdk.ConfigErrorException
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertFalse
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.assertThrows
import org.junit.jupiter.params.ParameterizedTest
import org.junit.jupiter.params.provider.ValueSource

class GcsWorkloadIdentityFederationConfigurationTest {

    private fun credential(
        extra: String = "",
        credentialSource: String = """{"file": "/var/run/secrets/token"}""",
    ) =
        """
        {
          "type": "external_account",
          "audience": "//iam.googleapis.com/projects/123/locations/global/workloadIdentityPools/pool/providers/provider",
          "subject_token_type": "urn:ietf:params:oauth:token-type:jwt",
          "token_url": "https://sts.googleapis.com/v1/token",
          "credential_source": $credentialSource
          $extra
        }
        """
            .trimIndent()

    private fun assertConfigError(json: String, messageFragment: String) {
        val e =
            assertThrows<ConfigErrorException> {
                GcsWorkloadIdentityFederationConfiguration.fromCredentialsJson(json)
            }
        assertTrue(
            e.message!!.contains(messageFragment),
            "expected '$messageFragment' in: ${e.message}",
        )
    }

    @Test
    fun `accepts a direct federated principal credential`() {
        val json = credential()
        assertEquals(
            json,
            GcsWorkloadIdentityFederationConfiguration.fromCredentialsJson(json).credentialsJson,
        )
    }

    @Test
    fun `accepts a URL credential source with service account impersonation`() {
        GcsWorkloadIdentityFederationConfiguration.fromCredentialsJson(
            credential(
                credentialSource =
                    """{"url": "http://token-proxy.default.svc.cluster.local/token", "format": {"type": "text"}}""",
                extra =
                    """, "service_account_impersonation_url": "https://iamcredentials.googleapis.com/v1/projects/-/serviceAccounts/sa@p.iam.gserviceaccount.com:generateAccessToken"""",
            ),
        )
    }

    @ParameterizedTest
    @ValueSource(strings = ["", "   "])
    fun `rejects blank input`(json: String) {
        assertConfigError(json, "requires a credential configuration")
    }

    @Test
    fun `rejects invalid JSON without echoing it`() {
        val e =
            assertThrows<ConfigErrorException> {
                GcsWorkloadIdentityFederationConfiguration.fromCredentialsJson(
                    """{"type": "external_account", "secret": "s3cr3t"""",
                )
            }
        assertTrue(e.message!!.contains("not valid JSON"))
        assertFalse(e.message!!.contains("s3cr3t"))
    }

    @Test
    fun `rejects a JSON value that is not an object`() {
        assertConfigError("[]", "must be a JSON object")
    }

    @Test
    fun `rejects a service account key`() {
        assertConfigError(
            """{"type": "service_account", "private_key": "x"}""",
            "found \"service_account\"",
        )
    }

    @Test
    fun `rejects a document without a type`() {
        assertConfigError("""{"audience": "x"}""", "no \"type\" field")
    }

    @ParameterizedTest
    @ValueSource(strings = ["audience", "subject_token_type", "credential_source"])
    fun `rejects a credential missing a required field`(field: String) {
        val json = credential().lines().filterNot { it.trimStart().startsWith("\"$field\"") }
        // Removing the last field leaves a trailing comma, so rebuild the object without it.
        val withoutField = json.joinToString("\n").replace(Regex(",\\s*}\\s*$"), "\n}")
        assertConfigError(withoutField, "missing the required \"$field\"")
    }

    @Test
    fun `rejects executable-sourced credentials`() {
        assertConfigError(
            credential(credentialSource = """{"executable": {"command": "/bin/sh -c id"}}"""),
            "Executable-sourced",
        )
    }

    @ParameterizedTest
    @ValueSource(
        strings =
            [
                "http://sts.googleapis.com/v1/token",
                "https://sts.example.com/v1/token",
                "https://sts.googleapis.com.example.com/v1/token",
                "https://user@sts.googleapis.com/v1/token",
                "not a url",
            ],
    )
    fun `rejects a token_url that is not an https googleapis endpoint`(url: String) {
        assertConfigError(
            credential().replace("https://sts.googleapis.com/v1/token", url),
            "\"token_url\"",
        )
    }

    @Test
    fun `rejects an impersonation url that is not an https googleapis endpoint`() {
        assertConfigError(
            credential(
                extra =
                    """, "service_account_impersonation_url": "https://attacker.example/generateAccessToken"""",
            ),
            "\"service_account_impersonation_url\"",
        )
    }

    @Test
    fun `toString does not leak the credential`() {
        val config = GcsWorkloadIdentityFederationConfiguration.fromCredentialsJson(credential())
        assertFalse(config.toString().contains("sts.googleapis.com"))
    }
}
