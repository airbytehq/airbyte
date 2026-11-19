/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.gcs_v2

import com.google.cloud.storage.StorageException
import java.io.IOException
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test

class GcsV2CheckerHintTest {
    private fun wif(e: Exception) = GcsV2Checker.wifHint("my-bucket", e)

    @Test
    fun `WIF 403 points at the bucket role`() {
        val hint = wif(StorageException(403, "caller does not have storage.objects.create access"))
        assertTrue("roles/storage.objectUser" in hint, hint)
        assertTrue("my-bucket" in hint, hint)
    }

    @Test
    fun `WIF 404 points at the bucket name`() {
        assertTrue("does not exist" in wif(StorageException(404, "Not Found")))
    }

    @Test
    fun `WIF 401 points at the audience`() {
        assertTrue("audience" in wif(StorageException(401, "Unauthorized")))
    }

    @Test
    fun `WIF status is found through wrapping exceptions`() {
        val wrapped = RuntimeException("upload failed", StorageException(403, "Forbidden"))
        assertTrue("roles/storage.objectUser" in wif(wrapped))
    }

    @Test
    fun `WIF token exchange failure points at the credential source`() {
        val hint = wif(StorageException(IOException("Error getting access token")))
        assertTrue("credential_source" in hint, hint)
    }

    @Test
    fun `HMAC signature error points at the key`() {
        val hint = GcsV2Checker.hmacHint("my-bucket", RuntimeException("SignatureDoesNotMatch"))
        assertTrue("HMAC key access ID or secret is wrong" in hint, hint)
    }
}
